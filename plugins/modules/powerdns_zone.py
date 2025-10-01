from __future__ import annotations
from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible_collections.aybarsm.utils.plugins.module_utils.swagger import Swagger, BaseAggregator as Aggregator
from ansible.module_utils.urls import fetch_url

Helper = Aggregator.tools.helper
Validate = Aggregator.tools.validate
Validator = Aggregator.tools.validator
Data = Aggregator.tools.data
json = Aggregator.tools.json

_swagger_config = {
    'settings': {
        'ansible': {
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
        'state': {'type': 'string', 'required': True, 'enum': ['list', 'retrieve', 'update', 'present', 'absent', 'rrsets']},
    },
    'remap': {
        'path.server_id': 'server_id',
        'path.zone_id': 'zone_id',
        'header.X-API-Key': 'api_key',
    },
}

def _prepare_rrsets(ret: dict)-> dict:
    Data.set(ret, 'data.rrsets', Data.get(ret, 'data.zone_struct.rrsets'))
    Data.forget(ret, 'data.zone_struct')
    
    return ret

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

    module = AnsibleModule(**module_kwargs)
    
    callback = None
    if state == 'rrsets':
        callback = _prepare_rrsets

    fetch_kwargs = swagger.prepare_execution(path, method, before_finalise = callback)
    url = fetch_kwargs.pop('url', '')
    
    # fetch_kwargs['type_data'] = type(fetch_kwargs['data']).__name__
    # path_debug = '/Users/aybarsm/PersonalSync/Coding/ansible/blrm/dev/debug_module.json'
    # Helper.save_as_json(fetch_kwargs, path_debug, overwrite=True, indent=2, ensure_ascii=False)

    
    resp, info = fetch_url(module, url, **fetch_kwargs)
    res = Helper.fetch_url_to_module_result(resp, info)
    
    if res['failed']:
        module.fail_json(res['msg'], **res['kwargs'])
        return

    ret = {
        'changed': fetch_kwargs['method'] not in ['GET', 'HEAD', 'OPTIONS'],
        'result': res['content'],
    }

    module.exit_json(**ret)

if __name__ == '__main__':
    main()