from ansible.module_utils.basic import AnsibleModule
from ansible_collections.aybarsm.utils.plugins.module_utils.swagger import PrimaryAggregator, Swagger

Helper = PrimaryAggregator.tools.helper

_swagger_config = {
    'ansible': {
        'validation': True,
        'load_params': True,
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
        'docs_validate_certs': 'docs_verify_ssl',
    },
}

def main():
    api = powerdns_api({
        'default_params': {
            'request_path': '/servers/{server_id}/zones/{zone_id}',
            'request_method': 'PATCH',
        },
        'mapping': {
            'path.server_id': 'server_id',
            'path.zone_id': 'zone_id',
            'body.zone_struct.rrsets.comments': 'comments',
            'body.zone_struct.rrsets.name': 'name',
            'body.zone_struct.rrsets.records.content': 'content',
            'body.zone_struct.rrsets.records.disabled': 'disabled',
            'body.zone_struct.rrsets.records.modified_at': 'modified_at',
            'body.zone_struct.rrsets.ttl': 'ttl',
            'body.zone_struct.rrsets.type': 'type',
        },
        'ignore': [
            'body.zone_struct',
            # 'body.zone_struct.api_rectify',
            # 'body.zone_struct.catalog',
            # 'body.zone_struct.dnssec',
            # 'body.zone_struct.edited_serial',
            # 'body.zone_struct.id',
            # 'body.zone_struct.kind',
            # 'body.zone_struct.master_tsig_key_ids',
            # 'body.zone_struct.masters',
            # 'body.zone_struct.name',
            # 'body.zone_struct.nameservers',
            # 'body.zone_struct.notified_serial',
            # 'body.zone_struct.nsec3narrow',
        ]
    })
    
    module = AnsibleModule(**api.arguments_default())
    # query = powerdns_api({
    #     'default_params': {
    #         'request_path': '/servers/{server_id}/zones/{zone_id}',
    #         'request_method': 'GET',
    #     }
    # })

    # ret = query.make_result()

    # module.exit_json(**{'response': api.arguments()['argument_spec'].get('api_key', 'NA')})
    module.exit_json(**{'response': {'mapping': api.mapping(), 'arg_spec': api.argument_spec()}})

if __name__ == '__main__':
    main()