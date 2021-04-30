=============================
Django AllAuth Saml2
=============================

.. image:: https://badge.fury.io/py/django-allauth-saml2.svg
    :target: https://badge.fury.io/py/django-allauth-saml2

Django allauth saml2 provider, this provider is based on pysaml2 (https://pysaml2.readthedocs.io/)

Quick start
-----------

1. Add "allauth_saml2" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'allauth_saml2',
    ]

    SOCIALACCOUNT_PROVIDERS = {
        'saml2': {
            # Metadata is required, choose either remote url or local file path
            'METADATA_AUTO_CONF_URL': 'The metadata configuration url',
            'METADATA_LOCAL_FILE_PATH': 'The metadata configuration file path',

            # EntityID populates the Issuer element in authn request Entity ID, optional, url of sp is used when missing
            # 'ENTITY_ID': 'https://mysite.com/saml2_auth/acs/', #

            # 'NAME_ID_FORMAT': FormatString, # Sets the Format property of authn NameIDPolicy element

            # encrypt/sign assertions
            # 'KEY_FILE': 'key.pem path',
            # 'CERT_FILE': 'cert.pem path',

            # 'ACCEPTED_TIME_DIFF':
        }
    }


Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
