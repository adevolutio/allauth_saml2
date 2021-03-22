from urllib.parse import urlparse

from saml2 import (
    BINDING_HTTP_POST,
    BINDING_HTTP_REDIRECT,
)
from saml2.client import Saml2Client as Saml2Client_
from saml2.config import Config as Saml2Config

import collections.abc


def update(d, u):
    """
    nested dict update
    https://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
    """
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = update(d.get(k, {}), v)
        else:
            d[k] = v
    return d


class Saml2Error(Exception):
    pass


class Saml2Client(object):
    def __init__(self, request, settings, acs_url):
        self.request = request
        self.settings = settings
        self.acs_url = acs_url
        self.state = None
        self.saml2_client = self.get_saml2_client()

    def __getattr__(self, name):
        return getattr(self.saml2_client, name)

    def get_saml2_client(self):
        saml_settings = self.get_saml2_config()

        sp_config = Saml2Config()
        sp_config.load(saml_settings)
        sp_config.allow_unknown_attributes = True
        saml_client = Saml2Client_(config=sp_config)

        return saml_client

    def get_saml2_config(self):
        """
        Configures a Saml2Client with the given settings

        SAML2 based SSO(Single-Sign-On) identity provider with dynamic metadata configuration

        https://pysaml2.readthedocs.io/en/latest/howto/config.html
        """

        saml_settings = {
            # "entityid": None,
            # "description": "Example SP",

            'service': {
                'sp': {
                    'endpoints': {
                        'assertion_consumer_service': [
                            (self.acs_url, BINDING_HTTP_REDIRECT),
                            (self.acs_url, BINDING_HTTP_POST)
                        ],
                        # Other Valid endpoints not configured yet
                        #'artifact_resolution_service': []
                        #"single_logout_service": []
                    },
                    # this is overriden if a key is available
                    'authn_requests_signed': False,

                    'allow_unsolicited': True,  # this is needed for POST

                    # Indicates that either the Authentication Response or the assertions contained
                    # within the response to this SP must be signed. Check DOCS
                    'want_assertions_signed': False,
                    'want_response_signed': False,
                    "want_assertions_or_response_signed": True,
                },
            },
        }

        if 'METADATA_LOCAL_FILE_PATH' in self.settings:
            update(saml_settings, {
                'metadata': {
                    'local': [self.settings['METADATA_LOCAL_FILE_PATH']]
                }
            })
        elif 'METADATA_AUTO_CONF_URL' in self.settings:
            update(saml_settings, {
                'metadata': {
                    'remote': [
                        {
                            "url": self.settings['METADATA_AUTO_CONF_URL'],
                        },
                    ]
                }
            })
        else:
            raise Saml2Error("IdP metadata missing")

        if 'ENTITY_ID' in self.settings:
            saml_settings['entityid'] = self.settings['ENTITY_ID']
        else:
            # EntityId: It is recommended that the entityid should point to a real webpage where the metadata
            # for the entity can be found. TODO: make this true
            uri = urlparse(self.acs_url)
            saml_settings['entityid'] = f'{uri.scheme}://{uri.netloc}'

        if 'NAME_ID_FORMAT' in self.settings:
            saml_settings['service']['sp']['name_id_format'] = self.settings['NAME_ID_FORMAT']

        if 'ACCEPTED_TIME_DIFF' in self.settings:
            saml_settings['accepted_time_diff'] = self.settings['ACCEPTED_TIME_DIFF']

        if 'KEY_FILE' in self.settings and 'CERT_FILE' in self.settings:
            try:
                from saml2.sigver import get_xmlsec_binary
            except ImportError:
                get_xmlsec_binary = None

            if get_xmlsec_binary:
                xmlsec_path = get_xmlsec_binary(["/opt/local/bin", "/usr/local/bin"])
            else:
                xmlsec_path = '/usr/local/bin/xmlsec1'

            update(saml_settings, {
                'service': {
                    'sp': {
                        "authn_requests_signed": True
                    }
                },
                "key_file": self.settings['KEY_FILE'],
                "cert_file": self.settings['CERT_FILE'],
                "xmlsec_binary": xmlsec_path,
            })

        # TODO: add encryption_keypairs

        return saml_settings
