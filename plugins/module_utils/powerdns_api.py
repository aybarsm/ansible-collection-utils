from typing import Any, Callable
from enum import Enum, auto
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.basic import env_fallback
from ansible_collections.aybarsm.utils.plugins.module_utils.tools import Data, Validate, Validator, Helper
from ansible_collections.aybarsm.utils.plugins.module_utils.swagger import Swagger

_DEFAULTS = {
    'swagger': {
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
        },
        'remap': {
            'header.X-API-Key': 'api_key',
        },
    }
}

# class Pdns(Enum):
#     Auth = auto()
#     Recursor = auto()
#     Dnsdist = auto()

class PdnsOperation(Enum):
    auth_zone = auto()

class PowerdnsApi():
    def __init__(self, op: PdnsOperation):
        self._meta = {'cfg': _DEFAULTS.copy()}
        self._swagger = Swagger(self.meta('cfg.swagger', {}))
        
        self._operation_set(op)
    
    def _get_value(self, container, key = '', default = None) -> Any:   
        return Data.get(container, key, default) if Validate.filled(key) else container
    
    def meta(self, key: str  = '', default: Any = None) -> Any:
        return self._get_value(self._meta, key, default)
    
    def _meta_set(self, key: str, value: Any) -> None:
        Data.set(self._meta, key, value)
    
    def _meta_forget(self, key: str) -> None:        
        Data.forget(self._meta, key)
    
    def meta_has(self, key: str) -> bool:
        return Data.has(self._meta, key)
    
    def swagger(self):
        return self._swagger
    
    def _operation_set(self, op: PdnsOperation) -> None:        
        docs_source = self._swagger.params('docs_source', '')
        if Validate.blank(docs_source):
            return
        
        self._swagger.load_swagger(docs_source)

        state = None
        match op:
            case PdnsOperation.auth_zone:
                self._swagger.cfg_set('defaults.server_id', {'_ansible': {'fallback': (env_fallback, ['PDNS_AUTH_API_SERVER_ID'])}})
                self._swagger.cfg_set('defaults.state', {'type': 'string', 'required': True, 'enum': ['list', 'retrieve', 'update', 'present', 'absent', 'rrsets']})
                self._swagger.remap_set('path.server_id', 'server_id')
                state = self._swagger.params('state', '')
                path = '/servers/{server_id}/zones'
                
                if state not in ['present', 'list']:
                    path += '/{zone_id}'
                    self._swagger.remap_set('path.zone_id', 'zone_id')
                
                match state:
                    case 'present':
                        method = 'POST'
                        self._swagger.remap_set('body.zone_struct', 'zone_struct')
                    case 'update':
                        method = 'PUT'
                        self._swagger.remap_set('body.zone_struct', 'zone_struct')
                        self._swagger.ignore_add('body.zone_struct.rrsets')
                    case 'rrsets':
                        method = 'PATCH'
                        self._swagger.remap_set('body.zone_struct.rrsets', 'rrsets')
                        self._swagger.ignore_add('body.zone_struct')
                    case 'absent':
                        method = 'DELETE'
                    case 'retrieve':
                        method = 'GET'
                        self._swagger.remap_set('query.rrsets', 'rrsets')
                        self._swagger.remap_set('query.rrset_name', 'rrset_name')
                        self._swagger.remap_set('query.rrset_type', 'rrset_type')
                        self._swagger.cfg_set('settings.remap.ignore_missing', True)
                    case 'list':
                        method = 'GET'
                        self._swagger.remap_set('query.zone', 'zone')
                        self._swagger.remap_set('query.dnssec', 'dnssec')
                        self._swagger.cfg_set('settings.remap.ignore_missing', True)
                    case _:
                        method = 'GET'
        ret = {
            'type': op,
            'path': path,
            'method': method,
            'before_finalise_callback': self._op_auth_zone_before_finalise_callback,
            'state': state,
            'valid': True,
        }
        self._meta_set('_.operation', ret.copy())
    
    def operation(self) -> dict:
        return self.meta('_.operation', {})

    def operation_type(self) -> PdnsOperation:
        return self.meta('_.operation.type', None)
    
    def operation_path(self) -> str:
        return self.meta('_.operation.path', None)

    def operation_method(self) -> str:
        return self.meta('_.operation.method', None)
    
    def operation_state(self) -> str:
        return self.meta('_.operation.state', None)
    
    def operation_before_finalise_callback(self) -> None | Callable:
        return self.meta('_.operation.before_finalise_callback', None)
    
    def is_operation_valid(self) -> bool:
        return self.meta('_.operation.valid', False) == True
    
    def get_ansible_module_arguments(self) -> dict:
        if not self.is_operation_valid():
            return {
                'argument_spec': self._swagger.prepare_validation_schema(cleanup=True),
            }

        kwargs = self._swagger.get_ansible_module_arguments(self.operation_path(), self.operation_method(), only_primary = True)

        if self.operation_type() == PdnsOperation.auth_zone and self.operation_state() == 'rrsets':
            Data.set(kwargs, 'argument_spec.rrsets.required', True)
        
        return kwargs
    
    def operation_execute(self, module) -> dict:
        path = self.operation_path()
        method = self.operation_method()
        ret = {
            'failed': True,
            'kwargs': {},
        }

        # The Ansible modules validator is highly unreliable:
        # Especially entries with default values and nested schemas.
        # So we provide primary entries only and then validate all parameters with Cerberus.
        schema = self._swagger.get_cerberus_validation_schema(self.operation_path(), self.operation_method())
        
        v = Validator(schema, allow_unknown = True) # type: ignore
        if v.validate(self._swagger.document()) != True: # type: ignore
            ret['msg'] = v.error_message()
            return ret
        
        before_finalise_callback = self.operation_before_finalise_callback()
        
        fetch_kwargs = self._swagger.prepare_execution(path, method, before_finalise = before_finalise_callback)
        url = fetch_kwargs.pop('url', '')

        ret = Helper.fetch_url_to_module_result(*fetch_url(module, url, **fetch_kwargs))

        if not ret['failed']:
            ret['changed'] = fetch_kwargs['method'] not in ['GET', 'HEAD', 'OPTIONS']
            del ret['failed']
        
        if self.operation_type() == PdnsOperation.auth_zone and self.operation_state() == 'retrieve':
            ret['result']['exists'] = ret['result']['status'] == 200
        
        return ret

    def _op_auth_zone_before_finalise_callback(self, ret: dict)-> dict:
        state = self.operation_state()
        if state == 'rrsets':
            Data.set(ret, 'data.rrsets', Data.get(ret, 'data.zone_struct.rrsets'))
            Data.forget(ret, 'data.zone_struct')
        elif state in ['present', 'update']:
            zone_struct = Data.get(ret, 'data.zone_struct', {})
            Data.set(ret, 'data', zone_struct.copy())
        
        return ret

