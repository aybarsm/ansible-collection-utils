from typing import Any, Optional, Mapping
from abc import ABC, abstractmethod
from ansible.errors import AnsibleActionFail
from ansible_collections.aybarsm.utils.plugins.module_utils.tools import Validate, Data, Str, Helper, Validator, PlayCache

_CONF = {
    'roles': {
        'fs': {
            'req_dirs': {
                'skip': ['/bin', '/boot', '/dev', '/etc', '/home', '/lib', '/lib64', '/mnt', '/media', '/opt', '/proc', '/root', '/run', '/sbin', '/srv', '/sys', '/tmp', '/usr', '/var']
            }
        }
    }
}

class PluginAction(ABC):
    def __init__(self, args: Mapping = {}, vars: Mapping = {}):
        self._meta = {'conf': _CONF.copy()}
        self._cache: Optional[PlayCache] = None
        self.set_op(args, vars)
    
    def _get_value(self, container, key = '', default = None)-> Any:
        return Data.get(container, key, default) if Validate.filled(key) else container

    def conf(self, key = '', default = None):
        return self._get_value(self._meta['conf'], key, default)
    
    def meta(self, key = '', default = None):
        return self._get_value(self._meta, key, default)
    
    def _meta_set(self, key, value):
        Data.set(self._meta, key, value)
    
    def _meta_forget(self, key):
        Data.forget(self._meta, key)
    
    def _meta_append(self, key, value, **kwargs)-> None:
        Data.append(self._meta, key, value, **kwargs)
    
    def _meta_prepend(self, key, value, **kwargs)-> None:
        Data.prepend(self._meta, key, value, **kwargs)
    
    def _has_meta(self, key):
        return Data.has(self._meta, key)

    def args(self, key = '', default = None):
        return self._get_value(self._meta['args'], key, default)

    def vars(self, key = '', default = None):
        return self._get_value(self._meta['vars'], key, default)

    def op(self, default: Any = None)-> Any:
        return self.args('op', default)

    def host(self, default: Any = None)-> Any:
        return self.vars('inventory_hostname', default)

    def host_vars(self, host, key = '', default = None):
        key = str(Str.start(key, 'hostvars.' + host + '.')).rstrip('.')
        return self.vars(key, default)
    
    def host_role_vars(self, host, key, default = None):
        meta_key = f'hosts.{host}.{key}'
        if Data.has(self._meta, meta_key):
            return self.meta(meta_key, default)
        
        key = Str.start(key, 'vars.')
        key = self.args(key, None)
        if key == None:
            return default
        
        ret = self.host_vars(host, key, default) #type: ignore
        
        Data.set(self._meta, meta_key, ret)

        return ret
    
    def play_batch(self, default: Any = None)-> Any:
        return self.vars('ansible_play_batch', default)
    
    def inventory(self, default: Any = None)-> Any:
        return self.vars('groups.all', default)
    
    def is_check_mode(self)-> bool:
        return self.vars('ansible_check_mode', False) == True

    def is_op(self, op: str):
        return self.op('op') == op
    
    def has_cache(self)-> bool:
        return self._cache != None

    def cache(self)-> Optional[PlayCache]:
        return self._cache
    
    def cache_set(self, key: str, value: Any)-> None:
        if not self._cache:
            return
        
        self._cache.set(key, value)
    
    def cache_forget(self, key: str)-> None:
        if not self._cache:
            return
        
        self._cache.forget(key)
    
    def cache_append(self, key: str, value: Any, **kwargs)-> None:
        if not self._cache:
            return
        
        self._cache.append(key, value, **kwargs)
    
    def cache_prepend(self, key: str, value: Any, **kwargs)-> None:
        if not self._cache:
            return
        
        self._cache.prepend(key, value, **kwargs)
    
    def set_op(self, args: Mapping = {}, vars: Mapping = {}):
        op = args.get('op', '')
        if Validate.blank(op):
            raise AnsibleActionFail('Operation argument op value cannot be blank')

        schema = self._get_validation_schema_operation(args, vars)
        if Validate.filled(schema):
            v = Validator(schema, allow_unknown = True) # type: ignore
            if v.validate(args) != True: # type: ignore
                Helper.dump(schema)
                raise AnsibleActionFail(v.error_message()) # type: ignore
            args = v.normalized(args) # type: ignore

        self._meta_set('args', dict(args).copy())
        self._meta_set('vars', dict(vars).copy())
        self._cache = PlayCache.make(vars)
        
    @abstractmethod
    def _get_validation_schema_operation(self, args, vars):
        pass