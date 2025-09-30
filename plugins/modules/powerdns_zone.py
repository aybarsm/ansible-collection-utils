from __future__ import annotations
from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.aybarsm.utils.plugins.module_utils.swagger import Swagger, Aggregator
from ansible.module_utils.urls import fetch_url

Helper = Aggregator.tools.helper
Validate = Aggregator.tools.validate
Data = Aggregator.tools.data

_swagger_config = {
    'settings': {
        'ansible': {
            'validation': True,
            'load_params': True,
        },
        'remap': {
            'ignore_missing': True,
        }
    },
    # 'defaults': {
    #     'url_base': {'_validation': {'fallback': (env_fallback, ['PDNS_API_URL_BASE'])}},
    #     'docs_source': {'_validation': {'fallback': (env_fallback, ['PDNS_API_DOCS_SOURCE'])}},
    #     'docs_validate_certs': {'_validation': {'fallback': (env_fallback, ['PDNS_API_DOCS_VALIDATE_CERTS'])}},
    #     'docs_cache_expires': {'_validation': {'fallback': (env_fallback, ['PDNS_API_DOCS_CACHE_EXPIRES'])}},
    #     'validate_certs': {'_validation': {'fallback': (env_fallback, ['PDNS_API_VALIDATE_CERTS'])}},
    #     'api_key': {'_validation': {'fallback': (env_fallback, ['PDNS_API_API_KEY'])}},
    #     'url_username': {'_validation': {'fallback': (env_fallback, ['PDNS_API_USERNAME'])}},
    #     'url_password': {'_validation': {'fallback': (env_fallback, ['PDNS_API_PASSWORD'])}},
    # },
    'remap': {
        'path.server_id': 'server_id',
        'path.zone_id': 'zone_id',
        'header.X-API-Key': 'api_key',
    },
}

def main():
    swagger = Swagger(_swagger_config)
    docs_source = swagger.params('docs_source', '')
    if Validate.blank(docs_source):
        module_arguments = {
            'argument_spec': swagger.prepare_validation_schema(True)
        }
    else:
        swagger.load_swagger(docs_source)
        module_arguments = swagger.get_ansible_module_arguments('/servers/{server_id}/zones/{zone_id}', 'get')

    module = AnsibleModule(**module_arguments)
    # module_arguments = {
    #     'argument_spec': swagger.prepare_validation_schema()
    # }
    # arg_spec = swagger.prepare_validation_schema(True)
    # arg_spec = Data.only_with(arg_spec, 'url_base', 'docs_source')
    # # module = AnsibleModule(**{'argument_spec': arg_spec})
    # module = AnsibleModule(**module_arguments)
    # module.exit_json(**{'response': {'arg_spec': swagger.prepare_validation_schema(True)}})

    module.exit_json(**{'response': {'ok': 'ok'}})

if __name__ == '__main__':
    main()