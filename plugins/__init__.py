from ansible_collections.aybarsm.utils.plugins.module_utils.tools import Aggregator as ToolsAggregator

_DEFAULTS_SWAGGER = {
    'remap_overwrite': False,
    'remap_ignore_missing': False,
    'segments': {
        'keys': ['path', 'query', 'header', 'body', 'form'],
        'defaults': {
            'type': 'dict',
            'required': False,
            'default': {},
        }
    },
    'extraction': {
        'ref_pattern': '.*\\.\\$ref.*$'
    },
    'ansible': {
        'validation': False,
        'load_params': False,
        'meta': {
            'kwargs': {
                'argument_spec': {
                    'url_base': {'env': True},
                    'docs_source': {'env': True},
                    'docs_validate_certs': {'env': True},
                    'docs_cache_expires': {'env': True},
                    'api_key': {'env': True},
                    'validate_certs': {'env': True},
                    'use_proxy': {'env': True},
                    'url_username': {'env': True},
                    'url_password': {'env': True},
                    'http_agent': {'env': True},
                    'force_basic_auth': {'env': True},
                    'client_cert': {'env': True},
                    'client_key': {'env': True},
                    'ca_path': {'env': True},
                    'use_gssapi': {'env': True},
                    'force': {'env': True},
                    'timeout': {'env': True},
                    'unix_socket': {'env': True},
                    'unredirected_headers': {'env': True},
                    'use_netrc': {'env': True},
                    'decompress': {'env': True},
                    'ciphers': {'env': True},
                },
            }
        },
        'defaults': {
            'kwargs': {
                'argument_spec': {
                    'url_base': {'type': 'str', 'required': True},
                    'docs_source': {'type': 'str', 'required': False},
                    'docs_validate_certs': {'type': 'bool', 'required': False, 'default': True},
                    'docs_cache_expires': {'type': 'int', 'required': False, 'default': 0},
                    'request_method': {'type': 'str', 'required': True, 'choices': ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS']},
                    'request_path': {'type': 'str', 'required': True},
                    'validate_certs': {'type': 'bool', 'required': False, 'default': True},
                    'use_proxy': {'type': 'bool', 'required': False, 'default': False},
                    'http_agent': {'type': 'str', 'required': False, 'default': ''},
                    'force_basic_auth': {'type': 'str', 'required': False, 'default': ''},
                    'client_cert': {'type': 'str', 'required': False, 'default': None},
                    'client_key': {'type': 'str', 'required': False, 'default': None},
                    'ca_path': {'type': 'str', 'required': False, 'default': None},
                    'use_gssapi': {'type': 'bool', 'required': False, 'default': False},
                    'force': {'type': 'bool', 'required': False, 'default': False},
                    'timeout': {'type': 'int', 'required': False, 'default': 10},
                    'unix_socket': {'type': 'str', 'required': False, 'default': None},
                    'unredirected_headers': {'type': 'list', 'required': False, 'default': None, 'elements': 'str'},
                    'use_netrc': {'type': 'bool', 'required': False, 'default': True},
                    'decompress': {'type': 'bool', 'required': False, 'default': True},
                    'ciphers': {'type': 'list', 'required': False, 'default': None, 'elements': 'str'},
                },
                'mutually_exclusive': [
                    ['docs_url', 'docs_content', 'docs_file'],
                    ['docs_content', 'docs_file', 'docs_validate_certs'],
                ],
                'required_one_of': [
                    ['docs_url', 'docs_content', 'docs_file'],
                ],
                'required_together': [],
                'required_if': [],
                'required_by': {},
                'add_file_common_args': False,
                'supports_check_mode': False,
            }
        }
    }
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