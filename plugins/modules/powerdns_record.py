from ansible.module_utils.basic import AnsibleModule
from ansible_collections.aybarsm.utils.plugins.module_utils.swagger import PrimaryAggregator, Swagger
from ansible.module_utils.basic import env_fallback

Helper = PrimaryAggregator.tools.helper

_swagger_config = {
    'settings': {
        'ansible': {
            'validation': True,
            'load_params': True,
        },
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
    api = Swagger(_swagger_config)
    module_arguments = api.get_ansible_module_arguments('/servers/{server_id}/zones/{zone_id}', 'patch')
    module = AnsibleModule(**module_arguments)
    
    module.exit_json(**{'response': {'ok': 'ok'}})

if __name__ == '__main__':
    main()