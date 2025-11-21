import typing as T
from abc import ABC, abstractmethod
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.fluent import Fluent
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.validator import Validator
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Convert, Data, Str, Validate, Utils
from ansible.plugins.action import ActionBase
from ansible.plugins.lookup import LookupBase

class RoleManager(ABC):
    def __init__(
        self, 
        args: T.Mapping[str, T.Any] = {}, 
        vars: T.Mapping[str, T.Any] = {},
        module: T.Optional[ActionBase|LookupBase] = None
    ):
        self.meta: Fluent = Fluent()
        self.container: Fluent = Fluent()
        self.args: Fluent = Fluent()
        self.vars: Fluent = Fluent()
        self.host_vars: dict[str, Fluent] = {}
        self.cache: Fluent = Fluent()
        self.ret: Fluent = Fluent()

        self.modules: dict[str, T.Optional[ActionBase | LookupBase]] = {
            'action': None,
            'lookup': None,
        }

        if module:
            self.set_module(module)
    
        self.set_op(args, vars)
        

        # if self._has_cache_file_path():
        #     self.cache = Cache.load(self._get_cache_file_path())
        #     self._meta_set('conf.cache.loaded', True)

    def set_op(self, args: T.Mapping[str, T.Any], vars: T.Mapping[str, T.Any]):
        op = args.get('op')
        if Validate.blank(op):
            raise ValueError('Operation argument op value cannot be blank')
        
        args = dict(self._template(args))
        
        schema = self._get_validation_schema_operation(args, vars)
        if Validate.filled(schema):
            v = Validator(schema, allow_unknown = True)
            if v.validate(args) != True:
                raise ValueError(v.error_message())
            args = v.normalized(args)

        vars = dict(vars)
        host_vars = dict(vars.get('hostvars', {}))
        if 'hostvars' in vars:
            del vars['hostvars']
        
        self.args = Fluent(args)
        self.vars = Fluent(vars)
        for host_, value_ in host_vars.items():
            self.host_vars[host_] = Fluent(dict(value_))

        self._resolve_tags()
        self._resolve_role_name()
    
    def get_module(self)-> T.Optional[ActionBase|LookupBase]:
        for module_ in self.modules.keys():
            if self.modules[module_]:
                return self.modules[module_]
        
        return None

    def set_module(self, module: ActionBase|LookupBase):
        if isinstance(module, ActionBase):
            self.modules['action'] = module
        elif isinstance(module, LookupBase):
            self.modules['lookup'] = module

    def get_result(self):
        op_name = self.op('')
        if Validate.filled(op_name) and Validate.object_has_method(self, op_name):
            getattr(self, op_name)()

        self.cache.save()

        return {'result': self.ret.all()}
    
    def _resolve_tags(self):
        if not self.meta.has('tags.run'):
            ansible_run_tags = list(self.vars.get('ansible_run_tags', []))
            module_run_tags = list(self.args.get('tags.run', []))
            self.meta.set('tags.run', list(set(ansible_run_tags + module_run_tags)))
        
        if not self.meta.has('tags.skip'):
            ansible_skip_tags = list(self.vars.get('ansible_skip_tags', []))
            module_skip_tags = list(self.args.get('tags.skip', []))
            self.meta.set('tags.skip', list(set(ansible_skip_tags + module_skip_tags)))
    
    def _resolve_role_name(self):
        role_name = self.__class__.__name__
        role_name = Str.case_snake(str(role_name).strip()).strip().strip('_')
        self.meta.set('role.name', role_name)
    
    def _template(self, data: T.Any, **kwargs)-> T.Any:
        if Validate.blank(data):
            return data

        if not self.get_module():
            raise RuntimeError('No module found to access templar')
        
        return Convert.from_ansible_template(self.get_module()._templar, data, **kwargs) #type: ignore

    def op(self, default: T.Any = '')-> T.Any:
        return self.args.get('op', default)

    def host(self, default: T.Any = None)-> T.Any:
        return self.vars.get('inventory_hostname', default)

    # def host_vars(self, host: str = '', key = '', default = None):
    #     if Validate.blank(host):
    #         host = self.host()
    #     key = str(Str.start(key, 'hostvars.' + host + '.')).rstrip('.')
    #     return self.vars(key, default)
    
    # def host_vars_has(self, host: str, key: str):
    #     return self.vars_has(str(Str.start(key, 'hostvars.' + host + '.')).rstrip('.'))
    
    # def host_ansible_facts(self, host: str = '', key = '', default = None):
    #     if Validate.blank(host):
    #         host = self.host()
    #     return self.vars(Str.start(Convert.to_data_key(key), f'hostvars.{host}.ansible_facts.'), default)
    
    # def host_role_vars(self, host, key, default = None):
    #     meta_key = f'hosts.{host}.{key}'
    #     if Data.has(self._meta, meta_key):
    #         return self.meta(meta_key, default)
        
    #     key = Str.start(key, 'vars.')
    #     key = self.args(key, None)
    #     if key == None:
    #         return default
        
    #     ret = self.host_vars(host, key, default) #type: ignore
        
    #     Data.set_(self._meta, meta_key, ret)

    #     return ret

    # def host_arg_vars(self, var: str, **kwargs)-> T.Any:
    #     default = kwargs.pop('default', None)
    #     var = self.args(f'vars.{var}', '')
    #     if Validate.blank(var):
    #         return default
        
    #     host = kwargs.pop('host', self.host())
    #     append = kwargs.pop('append', [])
    #     key_parts = ['hostvars', host, var]
    #     if Validate.filled(append):
    #         key_parts += list(append)

    #     key = Convert.to_data_key(*key_parts)

    #     return self.vars(key, default)
    
    # def play_batch(self, default: T.Any = None)-> T.Any:
    #     return self.vars('ansible_play_batch', default)
    
    # def inventory(self, **kwargs)-> list:
    #     inventory = list(self.vars('groups.all', []))
        
    #     if kwargs.pop('remote', False) == True:
    #         inventory = Data.difference(inventory, ['vars'])

    #     return inventory
    
    # def is_check_mode(self)-> bool:
    #     return self.vars('ansible_check_mode', False) == True

    # def is_op(self, op: str):
    #     return self.op('op') == op

    # def is_cache_loaded(self)-> bool:
    #     return Validate.is_truthy(self.meta('conf.cache.loaded'))
    
    # def _has_cache_file_path(self)-> bool:
    #     return Validate.filled(self._get_cache_file_path())
    
    # def _get_cache_file_path(self)-> str:
    #     return self.args('play.cache_file', '')

    # def tag_run_has(self, *terms: str, **kwargs)->bool:
    #     return Validate.contains(self.meta('_.tags.run', []), *terms, **kwargs)
    
    # def tag_skip_has(self, *terms: str, **kwargs)->bool:
    #     return Validate.contains(self.meta('_.tags.skip', []), *terms, **kwargs)
    
    # def mod_eligible(self, mod):
    #     return self.tag_eligible(mod)
    
    # def tag_eligible(self, tag):
    #     return self.tag_run_has('all', tag) and not self.tag_skip_has(tag)
    
    # @staticmethod
    # def item_eligible(item: T.Mapping)-> bool:
    #     return Data.get(item, '_skip', False) != True and Data.get(item, '_keep', True) != False
    
    # def is_host_in_play_batch(self, host: str)-> bool:
    #     return host in self.vars('ansible_play_batch', [])
    
    # def domain(self, host: str = '')-> str:
    #     if Validate.blank(host):
    #         host = self.host()
        
    #     return Data.first_filled(
    #         self.host_vars(host, '_domain'), 
    #         self.vars('_domain'), 
    #         'blrm'
    #     )
    
    # def _resolve_role_cfg(self, **kwargs)-> None:
    #     role_name = self.meta('role.name', '')
    #     if Validate.blank(role_name):
    #         return
        
    #     host = self.host()
    #     role_name = str(role_name).strip().strip('_').strip()
    #     role_cfg = {
    #         'main': {},
    #         'host': {},
    #         'all': {}
    #     }

    #     host_role_var_keys = Data.where(
    #         list(self.host_vars(host=host, default = {}).keys()),
    #         lambda var_name: str(var_name).startswith(f'{role_name}__')
    #     )

    #     for var_name in host_role_var_keys:
    #         cfg_key = Str.chop_start(var_name, f'{role_name}__')
    #         Data.set_(
    #             role_cfg, 
    #             f'host.{cfg_key}', 
    #             self._template(self.host_vars(host=host, key=var_name))
    #         )

    #     main_role_var_keys = Data.where(
    #         list(self.vars(default = {}).keys()),
    #         lambda var_name: str(var_name).startswith(f'{role_name}__')
    #     )

    #     for var_name in main_role_var_keys:
    #         cfg_key = Str.chop_start(var_name, f'{role_name}__')
    #         Data.set_(role_cfg, f'main.{cfg_key}', self._template(self.vars(key=var_name)))
        
    #     role_cfg['all'] = Data.combine(role_cfg['main'], role_cfg['host'], recursive=True)
        
    #     self._meta_set('role.cfg', Convert.as_copied(role_cfg))

    # def get_role_cfg(self, sub: str = 'all')-> Fluent:
    #     if Validate.blank(self.meta('role.cfg', {})):
    #         self._resolve_role_cfg()
        
    #     key_suffix = f'.{sub}' if sub in ['host', 'main', 'all'] else ''
    #     return Fluent(self.meta(f'role.cfg{key_suffix}', {}))
    
    # def _lookup(self, name: str, *args, **kwargs):
    #     if not self._action_module:
    #         raise RuntimeError('Action module does not exist to perform this')
        
    #     flat_ret = kwargs.pop('flat_ret', False)
    #     lookup = Data.get(self._container, f'lookup.{name}')
    #     if Validate.blank(lookup):
    #         from ansible.plugins.loader import lookup_loader
    #         lookup = lookup_loader.get(
    #             name,
    #             loader=self._action_module._loader,
    #             templar=self._action_module._templar,
    #         )

    #         Data.set_(self._container, f'lookup.{name}', Convert.as_copied(lookup))
        
    #     args = list(args)
    #     kwargs = dict(kwargs)
    #     kwargs['variables'] = Convert.as_copied(self.vars())

    #     ret = lookup.run(args, **kwargs)
    #     if Validate.truthy(flat_ret) and Validate.is_iterable(ret):
    #         ret = list(ret)[0]

    #     return ret
    
    # def _exec_cmd(self, *args, **kwargs):
    #     if not self._action_module:
    #         raise RuntimeError('Action module does not exist to perform this')
        
    #     return self._action_module._low_level_execute_command(*args, **kwargs)
    
    # def _exec_module(self, **kwargs):
    #     if not self._action_module:
    #         raise RuntimeError('Action module does not exist to perform this')
        
    #     kwargs = dict(kwargs)
    #     kwargs['task_vars'] = self.vars()

    #     return self._action_module._execute_module(**kwargs)

    # def _async_status(self, job: T.Mapping, **kwargs):
    #     if not self._action_module:
    #         raise RuntimeError('Action module does not exist to perform this')
        
    #     is_cleanup = kwargs.pop('is_cleanup', False)
    #     jid = Data.get(job, 'ansible_job_id')
    #     async_dir = Utils.fs_dirname(Data.get(job, 'results_file'))

    #     kwargs = dict(kwargs)
    #     kwargs['module_name'] = 'ansible.builtin.async_status'
    #     kwargs['module_args'] = {
    #         'jid': jid,
    #         '_async_dir': async_dir,
    #     }

    #     if is_cleanup:
    #         kwargs['module_args']['mode'] = 'cleanup'

    #     return self._exec_module(**kwargs)
    
    # def _async_cleanup(self, job: T.Mapping, **kwargs):
    #     kwargs['is_cleanup'] = True

    #     return self._async_status(job, **kwargs)

    # def set_cache(self, cache: Fluent)-> None:
    #     self.cache = Convert.as_copied(cache)
    
    # def get_action_module(self)-> T.Optional[ActionBase]:
    #     return self._action_module

    # def set_action_module(self, module: ActionBase)-> None:
    #     self._action_module = module
    
    # def has_action_module(self)-> bool:
    #     return Validate.filled(self._action_module)
    
    # def get_lookup_module(self)-> T.Optional[LookupBase]:
    #     return self._lookup_module

    # def set_lookup_module(self, module: LookupBase)-> None:
    #     self._lookup_module = module
    
    # def has_lookup_module(self)-> bool:
    #     return Validate.filled(self._lookup_module)

    # def get_play_meta(self)-> T.Mapping:
    #     return self.vars('blrm__facts.play', {})

    @abstractmethod
    def _get_validation_schema_operation(self, args, vars)-> dict:
        pass