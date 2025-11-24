import typing as T
from abc import ABC, abstractmethod
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.fluent import Fluent
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.validator import Validator
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Convert, Data, Factory, Str, Validate, Utils
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
        self.cache: Fluent = Fluent()
        self.ret: Fluent = Fluent()

        self.modules: dict[str, T.Optional[ActionBase | LookupBase]] = {
            'action': None,
            'lookup': None,
        }

        if module:
            self.set_module(module)
    
        self.set_op(args, vars)

        if Validate.object_has_method(self, '_calback_post_init'):
            getattr(self, '_calback_post_init')()

    def set_op(self, args: T.Mapping[str, T.Any], vars: T.Mapping[str, T.Any]) -> None:
        op = args.get('op')
        if Validate.blank(op):
            raise ValueError('Operation argument op value cannot be blank')

        if Validate.object_has_method(self, '_calback_pre_op'):
            getattr(self, '_calback_pre_op')()
        
        schema = self._get_operation_validation_schema(args, vars)
        
        if Validate.filled(schema):
            args = Convert.to_primitive(args)
            v = Validator(schema, allow_unknown = True)
            if v.validate(args) != True:
                raise ValueError(v.error_message())
            args = v.normalized(args)

        self.args = Fluent(args)
        self.vars = Fluent(vars)

        self._resolve_role_name()
        self._resolve_role_tags()
        self._resolve_role_cfg()

    def _resolve_role_tags(self):
        for type_ in ['run', 'skip']:
            if not self.meta.has(f'tags.{type_}'):
                continue

            self.meta.set(f'tags.{type_}', list(self.vars.get(f'ansible_{type_}_tags', [])))

            if self.args.filled(f'config.tags.{type_}'):
                self.meta.append(f'tags.{type_}', self.args.get(f'config.tags.{type_}'), extend=True, unique=True)
    
    def _resolve_role_name(self):
        if self.meta.has('role.name'):
            return

        role_name = self.__class__.__name__
        role_name = Str.case_snake(str(role_name).strip()).strip().strip('_')
        self.meta.set('role.name', role_name)
    
    def _resolve_role_cfg(self, **kwargs)-> None:
        if self.meta.has('role.cfg'):
            return
        
        role_name = self.meta.get('role.name', '')
        if Validate.blank(role_name):
            return
        
        host = self.host()
        role_name = str(role_name).strip().strip('_').strip()
        var_keys = Data.where(
            list(set(self.vars.keys() + list(self.host_vars(host, '', {}).keys()))),
            lambda entry: str(entry).startswith(f'{role_name}__'),
            default=[],
        )

        for var_name in var_keys:
            cfg_key = Str.chop_start(var_name, f'{role_name}__')
            self.meta.set(
                f'role.cfg.{cfg_key}',
                self.host_var_default(host, var_name)
            )
    
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
    
    def inventory(self, **kwargs) -> list[str]:
        inventory = list(self.vars.get('groups.all', []))
        
        if kwargs.pop('remote', False) == True:
            inventory = Data.difference(inventory, ['vars'])

        return inventory

    def host_vars(self, host: str, key: str, default: T.Any = None) -> T.Any:
        return self.vars.get(Convert.to_data_key('hostvars', host, key), default)
    
    def host_ansible_facts(self, host: str, key: str, default: T.Any = None) -> T.Any:
        return self.vars.get(Convert.to_data_key('hostvars', host, 'ansible_facts', key), default)

    def domain(self, host: str = '')-> str:
        if Validate.blank(host):
            host = self.host()
        
        return self.host_var_default(host, '_domain', 'blrm')
    
    def host_var_default(self, host: str, key: str, default: T.Any = None) -> T.Any:
        if self.vars.has(f'hostvars.{host}.{key}'):
            return self.vars.get(f'hostvars.{host}.{key}')
        else:
            return self.vars.get(key, default)
    
    def tag_eligible(self, *args, **kwargs):
        is_all = kwargs.pop('all', False) == True
        tags_run = self.meta.get('tags.run', [])
        tags_skip = self.meta.get('tags.skip', [])

        if not is_all:
            for tag in args:
                if ('all' in tags_run or tag in tags_run) and tag not in tags_skip:
                    return True
            
            return False

        return Validate.filled(Data.intersect(tags_run, list(set(list(args) + ['all'])))) and Validate.blank(Data.intersect(tags_skip, args))
    
    def is_op(self, op: str) -> bool:
        return self.op('op') == op
    
    @abstractmethod
    def _get_operation_validation_schema(self, args: T.Mapping[str, T.Any], vars: T.Mapping[str, T.Any]) -> dict:
        pass