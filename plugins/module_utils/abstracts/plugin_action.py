from typing import Any, Mapping
from abc import ABC, abstractmethod
from ansible_collections.aybarsm.utils.plugins.module_utils.tools import Validate, Data, Str, Helper, Validator

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
        self._meta = {'conf': _CONF.copy(), '_': {}}
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
    
    @staticmethod
    def _key(key: str = ''):
        return Helper.data_key(key.strip('.').strip('_').strip('.'))

    def _(self, key = '', default = None)-> Any:
        return self._get_value(self._meta['_'], self._key(key), default)

    def _set(self, key, value: Any)-> Any:
        return Data.set(self._meta['_'], self._key(key), value)
    
    def _forget(self, key)-> Any:
        return Data.forget(self._meta['_'], self._key(key))
    
    def _append(self, key, value: Any, **kwargs)-> Any:
        return Data.append(self._meta['_'], self._key(key), value, **kwargs)

    def _prepend(self, key, value: Any, **kwargs)-> Any:
        return Data.prepend(self._meta['_'], self._key(key), value, **kwargs)
    
    def _has(self, key)-> bool:
        return Data.has(self._meta['_'], self._key(key))

    def _filled(self, key)-> bool:
        return Validate.filled(self._(key))
    
    def _blank(self, key)-> bool:
        return Validate.blank(self._(key))

    def op(self, default: Any = None)-> Any:
        return self.args('op', default)

    def host(self, default: Any = None)-> Any:
        return self.vars('inventory_hostname', default)

    def host_vars(self, host: str = '', key = '', default = None):
        if Validate.blank(host):
            host = self.host()
        key = str(Str.start(key, 'hostvars.' + host + '.')).rstrip('.')
        return self.vars(key, default)
    
    def host_ansible_facts(self, host: str = '', key = '', default = None):
        if Validate.blank(host):
            host = self.host()
        return self.vars(Str.start(Helper.data_key(key), f'hostvars.{host}.ansible_facts.'), default)
    
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

    def host_arg_vars(self, var: str, **kwargs)-> Any:
        default = kwargs.pop('default', None)
        var = self.args(f'vars.{var}', '')
        if Validate.blank(var):
            return default
        
        host = kwargs.pop('host', self.host())
        append = kwargs.pop('append', [])
        key_parts = ['hostvars', host, var]
        if Validate.filled(append):
            key_parts += list(append)

        key = Helper.normalise_data_key(*key_parts)

        return self.vars(key, default)
    
    def play_batch(self, default: Any = None)-> Any:
        return self.vars('ansible_play_batch', default)
    
    def inventory(self, **kwargs)-> list:
        inventory = list(self.vars('groups.all', []))
        
        if kwargs.pop('remote', False) == True:
            inventory = Data.difference(inventory, ['vars'])

        return inventory
    
    def is_check_mode(self)-> bool:
        return self.vars('ansible_check_mode', False) == True

    def is_op(self, op: str):
        return self.op('op') == op
    
    def set_op(self, args: Mapping = {}, vars: Mapping = {}):
        op = args.get('op', '')
        if Validate.blank(op):
            raise ValueError('Operation argument op value cannot be blank')
        
        args = Helper.to_safe_json(args)
        schema = self._get_validation_schema_operation(args, vars)
        if Validate.filled(schema):
            v = Validator(schema, allow_unknown = True) # type: ignore
            if v.validate(args) != True: # type: ignore
                raise ValueError(v.error_message()) # type: ignore
            args = v.normalized(args) # type: ignore

        self._meta_set('args', dict(args).copy())
        self._meta_set('vars', dict(vars).copy())
        self._meta_set('_.tags.run', set(list(self.vars('ansible_run_tags', [])) + self.args('tags.run', []))) #type: ignore
        self._meta_set('_.tags.skip', set(list(self.vars('ansible_skip_tags', [])) + self.args('tags.skip', []))) #type: ignore
    
    def tag_run_has(self, *terms: str, **kwargs)->bool:
        return Validate.contains(self.meta('_.tags.run', []), *terms, **kwargs)
    
    def tag_skip_has(self, *terms: str, **kwargs)->bool:
        return Validate.contains(self.meta('_.tags.skip', []), *terms, **kwargs)
    
    def mod_eligible(self, mod):
        return self.tag_run_has('all', mod) and not self.tag_skip_has(mod)
    
    @staticmethod
    def item_eligible(item: Mapping)-> bool:
        return Data.get(item, '_skip', False) != True and Data.get(item, '_keep', True) != False
    
    def is_host_in_play_batch(self, host: str)-> bool:
        return host in self.vars('ansible_play_batch', [])
    
    def domain(self, host: str = '')-> str:
        if Validate.blank(host):
            host = self.host()
        return Helper.first_filled(self.host_vars(host, '_domain'), self.vars('_domain'), 'blrm')

    @abstractmethod
    def _get_validation_schema_operation(self, args, vars):
        pass