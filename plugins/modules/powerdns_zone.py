from __future__ import annotations
from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.aybarsm.utils.plugins.module_utils.swagger import Swagger, Aggregator
from ansible.module_utils.urls import fetch_url

Helper = Aggregator.tools.helper
Validate = Aggregator.tools.validate
Validator = Aggregator.tools.validator
Data = Aggregator.tools.data
json = Aggregator.tools.json

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
        # 'url_base': {'_validation': {'fallback': (env_fallback, ['PDNS_API_URL_BASE'])}},
        # 'docs_source': {'_validation': {'fallback': (env_fallback, ['PDNS_API_DOCS_SOURCE'])}},
        # 'docs_validate_certs': {'_validation': {'fallback': (env_fallback, ['PDNS_API_DOCS_VALIDATE_CERTS'])}},
        # 'docs_cache_expires': {'_validation': {'fallback': (env_fallback, ['PDNS_API_DOCS_CACHE_EXPIRES'])}},
        # 'validate_certs': {'_validation': {'fallback': (env_fallback, ['PDNS_API_VALIDATE_CERTS'])}},
        # 'api_key': {'_validation': {'fallback': (env_fallback, ['PDNS_API_API_KEY'])}},
        # 'url_username': {'_validation': {'fallback': (env_fallback, ['PDNS_API_USERNAME'])}},
        # 'url_password': {'_validation': {'fallback': (env_fallback, ['PDNS_API_PASSWORD'])}},
        'state': {'type': 'string', 'required': True, 'enum': ['list', 'retrieve', 'update', 'present', 'absent', 'rrsets']},
    },
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
        module = AnsibleModule(**module_arguments)
        return
    
    swagger.load_swagger(docs_source)
    state = swagger.params('state', '')
    
    path = '/servers/{server_id}/zones/{zone_id}'

    if state == 'absent':
        method = 'delete'
    elif state == 'present':
        path = '/servers/{server_id}/zones'
        method = 'post'
        swagger.remap_set('body.zone_struct', 'zone')
    elif state == 'update':
        method = 'put'
        swagger.remap_set('body.zone_struct', 'zone')
    elif state == 'list':
        path = '/servers/{server_id}/zones'
        method = 'get'
    elif state == 'rrsets':
        method = 'patch'
        swagger.remap_set('body.zone_struct.rrsets', 'rrsets')
        swagger.ignore_add('body.zone_struct')
    else:
        method = 'get'

    module_kwargs = swagger.get_ansible_module_arguments(path, method, only_primary = True)

    if state == 'rrsets':
        Data.set(module_kwargs, 'argument_spec.rrsets.required', True)
    
    module = AnsibleModule(**module_kwargs)

    schema = swagger.get_cerberus_validation_schema(path, method)
    
    v = Validator(schema, allow_unknown = True) # type: ignore
    if v.validate(swagger.document()) != True: # type: ignore
        module.fail_json(msg=v.error_message()) # type: ignore
    
    swagger.params_combine(v.normalized(swagger.document()), recursive=True)

    # save_json = {
    #     'module_kwargs': module_kwargs,
    #     'primary_key_types': {}
    # }
    
    # for primary_key in module_kwargs['argument_spec'].keys():
    #     dest = f'argument_spec.{primary_key}'
    #     type_ = Data.get(module_kwargs, f'{dest}.type', '')
    #     has_options = Data.has(module_kwargs, f'{dest}.options')
    #     if type_ not in ['dict', 'list'] or not has_options:
    #         continue
        
    #     Data.set(save_json, f'{dest}.options', type_)
    #     Data.forget(module_kwargs, f'{dest}.options')
        # if type_ in ['dict', 'list'] and 'options' in module_kwargs['argument_spec'][primary_key]:
            # Data.set(save_json, f'primary_key_types.{primary_key}', type_)
            # Data.set(save_json, f'primary_key_types.{primary_key}', type_)
            # module_kwargs = Data.all_except(module_kwargs, f'primary_key_types.{primary_key}.options')
            # del module_kwargs['argument_spec'][primary_key]['options']
        # Data.set(save_json, f'primary_key_types.{primary_key}', module_kwargs['argument_spec'][primary_key]['type'])

    # path_debug = '/Users/aybarsm/PersonalSync/Coding/ansible/blrm/dev/debug_module.json'
    # Helper.save_as_json(save_json, path_debug, overwrite = True, indent=2, ensure_ascii=False)

    # module = AnsibleModule(**module_kwargs)
    # fetch_kwargs = swagger.prepare_execution(path, method)

    # url = fetch_kwargs.pop('url', '')
    # resp, info = fetch_url(module, url, **fetch_kwargs)
    # res = Helper.fetch_url_to_module_result(resp, info)

    
    # if res['fail']:
    #     module.fail_json(*res['args'], **res['kwargs'])
    #     return

    # ret = {
    #     'changed': fetch_kwargs['method'] not in ['GET', 'HEAD', 'OPTIONS'],
    #     'result': res['content'],
    # }

    module.exit_json(**{'response': 'ok'})

if __name__ == '__main__':
    main()