from ansible_collections.aybarsm.utils.plugins.module_utils.tools import Aggregator as ToolsAggregator

_DEFAULTS_SWAGGER = {
    # '_': {
    #     'defaults': {
    #         'path': {'type': 'object', 'required': False, 'default': {}},
    #         'query': {'type': 'object', 'required': False, 'default': {}},
    #         'header': {'type': 'object', 'required': False, 'default': {}},
    #         'body': {'type': 'object', 'required': False, 'default': {}},
    #         'form': {'type': 'object', 'required': False, 'default': {}},
    #     },
    # },
    'settings': {
        'extraction': {
            'ref_pattern': '.*\\.\\$ref.*$',
        },
        'remap': {
            'overwrite': False,
            'ignore_missing': False,
        },
        'combine': {
            'ansible': {
                'kwargs': {
                    'recursive': True,
                    'list_merge': 'prepend_rp',
                },
            },
        },
        'ansible': {
            'validation': False,
            'load_params': False,
            'kwargs': {
                'argument_spec': {},
                'mutually_exclusive': [],
                'required_one_of': [],
                'required_together': [],
                'required_if': [],
                'required_by': {},
                'add_file_common_args': False,
                'supports_check_mode': False,
            },
        },
    },
    'defaults': {
        'url_base': {'type': 'string', 'required': True},
        'docs_source': {'type': 'string', 'required': True},
        'docs_validate_certs': {'type': 'boolean', 'required': False, 'default': True},
        'docs_cache_expires': {'type': 'integer', 'required': False, 'default': 0},
        'url_username': {'type': 'string', 'required': True},
        'url_password': {'type': 'string', 'required': True},
        'validate_certs': {'type': 'boolean', 'required': False, 'default': True},
        'use_proxy': {'type': 'boolean', 'required': False, 'default': False},
        'http_agent': {'type': 'string', 'required': False, 'default': ''},
        'force_basic_auth': {'type': 'string', 'required': False, 'default': ''},
        'client_cert': {'type': 'string', 'required': False, 'default': None},
        'client_key': {'type': 'string', 'required': False, 'default': None},
        'ca_path': {'type': 'string', 'required': False, 'default': None},
        'use_gssapi': {'type': 'boolean', 'required': False, 'default': False},
        'force': {'type': 'boolean', 'required': False, 'default': False},
        'timeout': {'type': 'integer', 'required': False, 'default': 10},
        'unix_socket': {'type': 'string', 'required': False, 'default': None},
        'unredirected_headers': {'type': 'array', 'required': False, 'default': None, 'items': {'type': 'string'}},
        'use_netrc': {'type': 'boolean', 'required': False, 'default': True},
        'decompress': {'type': 'boolean', 'required': False, 'default': True},
        'ciphers': {'type': 'array', 'required': False, 'default': None, 'items': {'type': 'string'}},
    },
}

def _collection_config() -> dict:
    path_root = ToolsAggregator.pathlib.Path(__file__).parent.parent
    return {
        'path': {
            'dir': {
                'root': str(path_root),
                'tmp' : str(path_root.joinpath('.tmp')),
            }
        },
        'defaults': {
            'swagger': _DEFAULTS_SWAGGER
        }
    }

class Aggregator:
    tools = ToolsAggregator
    config = _collection_config()