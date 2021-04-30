from allauth.utils import import_attribute
from django.urls import include, path


def default_urlpatterns(provider):
    login_view = import_attribute(provider.get_package() + ".views.saml2_login")
    acs_view = import_attribute(provider.get_package() + ".views.saml2_acs")

    urlpatterns = [
        path("login/", login_view, name=provider.id + "_login"),
        # TODO: change to login/acs to keep allauth convention
        path("acs/", acs_view, name=provider.id + "_acs"),
    ]

    return [path(provider.get_slug() + "/", include(urlpatterns))]
