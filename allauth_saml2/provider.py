from allauth.socialaccount.providers.base import Provider
from django.urls import reverse


# noinspection PyAbstractClass
class Saml2Provider(Provider):
    id = ''

    mappings = {
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/upn': 'upn',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress': 'email',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname': 'first_name',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname': 'last_name',
        'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name': 'name',
    }

    def convert_from_mapping(self, data):
        fields = {}
        for key in data:
            if key in self.mappings:
                fields[self.mappings[key]] = data[key][0]
            else:
                fields[key] = data[key][0]
        return fields

    def get_login_url(self, request, **kwargs):
        url = reverse(self.id + "_login")
        # if kwargs:
        #     url = url + "?" + urlencode(kwargs)
        return url
