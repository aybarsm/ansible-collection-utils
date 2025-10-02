from ansible.module_utils.basic import env_fallback
from ansible_collections.aybarsm.utils.plugins.module_utils.tools import Data
from ansible_collections.aybarsm.utils.plugins.module_utils import Swagger

_DEFAULTS = {
    'settings': {
        'ansible': {
            'load_params': True,
        },
    },
    'defaults': {
        'url_base': {'_ansible': {'fallback': (env_fallback, ['PDNS_AUTH_API_URL_BASE'])}},
        'docs_source': {'_ansible': {'fallback': (env_fallback, ['PDNS_AUTH_API_DOCS_SOURCE'])}},
        'docs_validate_certs': {'_ansible': {'fallback': (env_fallback, ['PDNS_AUTH_API_DOCS_VALIDATE_CERTS'])}},
        'docs_cache_expires': {'_ansible': {'fallback': (env_fallback, ['PDNS_AUTH_API_DOCS_CACHE_EXPIRES'])}},
        'validate_certs': {'_ansible': {'fallback': (env_fallback, ['PDNS_AUTH_API_VALIDATE_CERTS'])}},
        'api_key': {'_ansible': {'fallback': (env_fallback, ['PDNS_AUTH_API_API_KEY'])}},
        'url_username': {'_ansible': {'fallback': (env_fallback, ['PDNS_AUTH_API_USERNAME'])}},
        'url_password': {'_ansible': {'fallback': (env_fallback, ['PDNS_AUTH_API_PASSWORD'])}},
    },
    'remap': {
        'header.X-API-Key': 'api_key',
    },
}

class PowerdnsApi():
    def __init__(self, cfg: dict = {}):
        cfg = Data.combine(_DEFAULTS, cfg, recursive = True)
        self._meta = {'cfg': cfg}
        self._swagger = Swagger()(cfg)