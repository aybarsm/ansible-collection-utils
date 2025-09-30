from __future__ import annotations
from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.aybarsm.utils.plugins.module_utils.swagger import Swagger, Aggregator

Helper = Aggregator.tools.helper
Validate = Aggregator.tools.validate

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
    'defaults': {
        'url_base': {'_validation': {'fallback': (env_fallback, ['PDNS_API_URL_BASE'])}},
        'docs_source': {'_validation': {'fallback': (env_fallback, ['PDNS_API_DOCS_SOURCE'])}},
        'docs_validate_certs': {'_validation': {'fallback': (env_fallback, ['PDNS_API_DOCS_VALIDATE_CERTS'])}},
        'docs_cache_expires': {'_validation': {'fallback': (env_fallback, ['PDNS_API_DOCS_CACHE_EXPIRES'])}},
        'validate_certs': {'_validation': {'fallback': (env_fallback, ['PDNS_API_VALIDATE_CERTS'])}},
        'api_key': {'_validation': {'fallback': (env_fallback, ['PDNS_API_API_KEY'])}},
        'url_username': {'_validation': {'fallback': (env_fallback, ['PDNS_API_USERNAME'])}},
        'url_password': {'_validation': {'fallback': (env_fallback, ['PDNS_API_PASSWORD'])}},
    },
    'remap': {
        'path.server_id': 'server_id',
        'path.zone_id': 'zone_id',
        'header.X-API-Key': 'api_key',
        'body.zone_struct.rrsets.comments': 'comments',
        'body.zone_struct.rrsets.name': 'name',
        'body.zone_struct.rrsets.changetype': 'changetype',
        'body.zone_struct.rrsets.records.content': 'content',
        'body.zone_struct.rrsets.records.disabled': 'disabled',
        'body.zone_struct.rrsets.records.modified_at': 'modified_at',
        'body.zone_struct.rrsets.ttl': 'ttl',
        'body.zone_struct.rrsets.type': 'type',
    },
    'ignore': [
        'body.zone_struct'
    ],
}

def main():
    swagger = Swagger(_swagger_config)
    docs_source = swagger.params('docs_source', '')
    if Validate.blank(docs_source):
        module_arguments = {
            'argument_spec': swagger.prepare_validation_schema()
        }
    else:
        swagger.load_swagger(docs_source)
        module_arguments = swagger.get_ansible_module_arguments('/servers/{server_id}/zones/{zone_id}', 'patch')

    # module = AnsibleModule(**module_arguments)
    # module_arguments = {
    #     'argument_spec': {
    #         'test_me': {
    #             'type': 'str',
    #             'required': True,
    #         }
    #     }
    # }
    module = AnsibleModule(**module_arguments)
    
    module.exit_json(**{'response': {'params': swagger.params()}})

if __name__ == '__main__':
    main()