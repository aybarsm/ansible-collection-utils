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
    },
}

def main():
    from ansible.module_utils.basic import AnsibleModule
    from ansible_collections.aybarsm.utils.plugins.module_utils.swagger import PrimaryAggregator, Swagger
    swagger = Swagger()

    module = AnsibleModule(argument_spec = {'test_me': {'type': 'str', 'required': True}})
    # module.exit_json(**{'response': {'loaded': jinja.loaded(), 'errors': jinja.errors()}})
    # module.exit_json(**{'response': test_undefined(testme)})
    module.exit_json(**{'response': {'ok': 'ok'}})

if __name__ == '__main__':
    main()
