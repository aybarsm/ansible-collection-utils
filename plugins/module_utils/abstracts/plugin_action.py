from plugins.module_utils import Aggregator as PrimaryAggregator

Validate = PrimaryAggregator.tools.validate
Data = PrimaryAggregator.tools.data
Str = PrimaryAggregator.tools.str
Helper = PrimaryAggregator.tools.helper
ABC = PrimaryAggregator.tools.abc.ABC
AnsibleActionFail = PrimaryAggregator.tools.ansible_errors.AnsibleActionFail
abstractmethod = PrimaryAggregator.tools.abc.abstractmethod

class PluginAction(ABC):
    def __init__(self, action, vars):
        self._meta = {}
        self._vars = {}
        self._args = {}
        self.set_op(action, vars)
    
    def _get_value(self, container, key = '', default = None):
        return Data.get(container, key, default) if Validate.filled(key) else container
    
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
    
    def vars(self, key = '', default = None):
        return self._get_value(self._vars, key, default)
    
    def args(self, key = '', default = None):
        return self._get_value(self._args, key, default)
    
    def meta(self, key = '', default = None):
        return self._get_value(self._meta, key, default)
    
    def _set_meta(self, key, value):
        Data.set(self._meta, key, value)
    
    def _forget_meta(self, key):
        Data.forget(self._meta, key)
    
    def _append_meta(self, key, value):
        current = self.meta(key, [])
        current.append(value) #type: ignore
        Data.set(self._meta, key, current)
    
    def _has_meta(self, key):
        return Data.has(self._meta, key)
    
    def op(self):
        return self.meta('op', '')

    def host(self):
        return self.meta('host', '')
    
    def play_batch(self):
        return self.vars('ansible_play_batch')
    
    def inventory(self):
        return self.vars('groups.all')
    
    def play_hash(self):
        if Validate.blank(self.meta('play.hash')):
            self._set_meta('play.hash', Str.to_md5('|'.join(self._play_hash_parts())))
                           
        return str(self.meta('play.hash'))
    
    def is_check_mode(self):
        return self.vars('ansible_check_mode', False)
    
    def _play_hash_parts(self):
        if Validate.blank(self.meta('play.hash_parts')):
            self._set_meta('play.hash_parts', [
                self.vars('ansible_play_name'),
                (','.join(self.vars('ansible_play_batch'))),
                Helper.ts().strftime('%Y%m%dT%H%M%S.%fZ'), # type: ignore
            ])
        
        return self.meta('play.hash_parts')

    def cache_file_path(self):
        parts = [
            'action',
            self.__class__.__name__,
            self._play_hash_parts()[-1],
            self.play_hash()
        ]
        
        file_name = ('_'.join(parts)) + '.json'
        
        return Helper.path_tmp(file_name)
    
    def set_op(self, action, vars):
        args = action._task.args.copy()
        op = args.get('op', '')
        if Validate.blank(op):
            raise AnsibleActionFail('Operation argument op value cannot be blank')

        schema = self._get_validation_schema_operation(args, vars)
        if Validate.filled(schema):
            v = Validator(schema, allow_unknown = True) # type: ignore
            if v.validate(args) != True: # type: ignore
                raise AnsibleActionFail(v.errors) # type: ignore
            self._args = v.normalized(args) # type: ignore
        else:
            self._args = args

        self._vars = vars
        self._action = action
        host = vars.get('inventory_hostname')
        self._set_meta('op', op)
        self._set_meta('host', host)

    def is_op(self, op):
        return self.meta('op', '') == op
    
    def reset(self):
        self._args = {}
        self._vars = {}
        self._action = None
        
    @abstractmethod
    def _get_validation_schema_operation(self, args, vars):
        pass