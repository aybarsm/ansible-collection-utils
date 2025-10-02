from __future__ import annotations
from ansible.module_utils.basic import AnsibleModule, env_fallback
from ansible.module_utils.urls import fetch_url
from ansible_collections.aybarsm.utils.plugins.module_utils.swagger import Swagger, PassThroughAggregator as Aggregator

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
        'url_base': {'_ansible': {'fallback': (env_fallback, ['PDNS_AUTH_API_URL_BASE'])}},
        'docs_source': {'_ansible': {'fallback': (env_fallback, ['PDNS_AUTH_API_DOCS_SOURCE'])}},
        'docs_validate_certs': {'_ansible': {'fallback': (env_fallback, ['PDNS_AUTH_API_DOCS_VALIDATE_CERTS'])}},
        'docs_cache_expires': {'_ansible': {'fallback': (env_fallback, ['PDNS_AUTH_API_DOCS_CACHE_EXPIRES'])}},
        'validate_certs': {'_ansible': {'fallback': (env_fallback, ['PDNS_AUTH_API_VALIDATE_CERTS'])}},
        'api_key': {'_ansible': {'fallback': (env_fallback, ['PDNS_AUTH_API_API_KEY'])}},
        'url_username': {'_ansible': {'fallback': (env_fallback, ['PDNS_AUTH_API_USERNAME'])}},
        'url_password': {'_ansible': {'fallback': (env_fallback, ['PDNS_AUTH_API_PASSWORD'])}},
        'server_id': {'_ansible': {'fallback': (env_fallback, ['PDNS_AUTH_API_SERVER_ID'])}},
        'state': {'type': 'string', 'required': True, 'enum': ['list', 'retrieve', 'update', 'present', 'absent', 'rrsets']},
    },
    'remap': {
        'path.server_id': 'server_id',
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
        module = AnsibleModule(argument_spec=swagger.prepare_validation_schema(cleanup=True))
        return
    
    swagger.load_swagger(docs_source)
    state = swagger.params('state', '')
    
    path = '/servers/{server_id}/zones'
    before_finalise_callback = None
    
    if state not in ['present', 'list']:
        path += '/{zone_id}'
        swagger.remap_set('path.zone_id', 'zone_id')
    
    match state:
        case 'present':
            method = 'post'
            swagger.remap_set('body.zone_struct', 'zone_struct')
        case 'update':
            method = 'put'
            swagger.remap_set('body.zone_struct', 'zone_struct')
        case 'rrsets':
            method = 'post'
            swagger.remap_set('body.zone_struct.rrsets', 'rrsets')
            swagger.ignore_add('body.zone_struct')
            before_finalise_callback = _prepare_rrsets
        case 'absent':
            method = 'delete'
        case _:
            method = 'get'

    module_kwargs = swagger.get_ansible_module_arguments(path, method, only_primary = True)

    if state == 'rrsets':
        Data.set(module_kwargs, 'argument_spec.rrsets.required', True)
    
    # The Ansible modules validator is highly unreliable:
    # Especially entries with default values and nested schemas.
    # So we provide primary entries only and then validate all parameters with Cerberus.
    module = AnsibleModule(**module_kwargs)
    schema = swagger.get_cerberus_validation_schema(path, method)
    
    v = Validator(schema, allow_unknown = True) # type: ignore
    if v.validate(swagger.document()) != True: # type: ignore
        module.fail_json(msg=v.error_message()) # type: ignore
    
    swagger.params_combine(v.normalized(swagger.document()), recursive=True) # type: ignore

    module = AnsibleModule(**module_kwargs)

    fetch_kwargs = swagger.prepare_execution(path, method, before_finalise = before_finalise_callback)
    url = fetch_kwargs.pop('url', '')
    
    res = Helper.fetch_url_to_module_result(*fetch_url(module, url, **fetch_kwargs))
    
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