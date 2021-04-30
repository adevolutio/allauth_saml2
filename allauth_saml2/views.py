from importlib import import_module

from allauth.exceptions import ImmediateHttpResponse
from allauth.socialaccount import providers
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.utils import build_absolute_uri
from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from saml2 import SAMLError, entity
from saml2.response import StatusError

from .client import Saml2Client, Saml2Error


class Saml2Adapter(object):
    provider_id = ""

    def __init__(self, request):
        self.request = request

    def get_provider(self):
        return providers.registry.by_id(self.provider_id, self.request)

    # noinspection PyUnusedLocal
    def complete_login(self, request, app, user_identity):
        login = self.get_provider().sociallogin_from_response(request, user_identity)
        return login

    def get_acs_url(self, request):
        callback_url = reverse(self.provider_id + "_acs")
        return build_absolute_uri(request, callback_url)


class Saml2View(object):
    def dispatch(self, request, *args, **kwargs):
        raise NotImplementedError

    @classmethod
    def adapter_view(cls, adapter):
        @csrf_exempt
        def view(request, *args, **kwargs):
            self = cls()
            self.request = request
            self.adapter = adapter(request)
            try:
                return self.dispatch(request, *args, **kwargs)
            except ImmediateHttpResponse as e:
                return e.response

        return view

    def get_client(self, request):
        acs_url = self.adapter.get_acs_url(request)
        provider = self.adapter.get_provider()
        provider_settings = provider.get_settings()
        client = Saml2Client(request, provider_settings, acs_url)
        return client


class Saml2LoginView(Saml2View):
    def dispatch(self, request, *args, **kwargs):
        provider = self.adapter.get_provider()
        client = self.get_client(request)

        # we store the session_key in relay_state to restore after login
        _, info = client.prepare_for_authenticate(
            relay_state=request.session.session_key
        )

        redirect_url = None

        # TODO: there mus be a better way of doing this
        for key, value in info["headers"]:
            if key == "Location":
                redirect_url = value
                break

        try:
            return HttpResponseRedirect(redirect_url)
        except ValueError as e:
            return render_authentication_error(request, provider.id, exception=e)


class Saml2ACSView(Saml2View):
    def dispatch(self, request, *args, **kwargs):
        provider = self.adapter.get_provider()
        app = provider.get_app(request)
        client = self.get_client(request)

        try:
            resp = request.POST.get("SAMLResponse", None)
            if resp is None:
                raise Saml2Error("No SAMLResponse in request")

            try:
                authn_response = client.parse_authn_request_response(
                    resp, entity.BINDING_HTTP_POST
                )
            except (SAMLError, StatusError, Exception):
                raise

            if authn_response is None:
                raise Saml2Error("AuthnResponse missing")

            try:
                user_identity = authn_response.get_identity()
            except ValueError:
                raise

            if user_identity == {}:
                raise Saml2Error("No user attributes in AuthnResponse")

            # if we get the session_key in the relaystate we restore the session
            session_key = request.POST.get("RelayState", None)
            if session_key:
                engine = import_module(settings.SESSION_ENGINE)
                request.session = engine.SessionStore(session_key)

            login = self.adapter.complete_login(request, app, user_identity)

            return complete_social_login(request, login)
        except (Saml2Error, SAMLError, StatusError, Exception) as e:

            return render_authentication_error(
                request, self.adapter.provider_id, exception=e
            )
