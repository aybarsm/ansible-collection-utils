import typing as t
from abc import ABC, abstractmethod
from ansible.plugins.action import ActionBase
from ansible.plugins.lookup import LookupBase
from ansible_collections.aybarsm.utils.plugins.module_utils.support.definitions import CommandModel
from ansible_collections.aybarsm.utils.plugins.module_utils.aggregator import Kit
from ansible_collections.aybarsm.utils.plugins.module_utils.support.fluent import Fluent
from ansible_collections.aybarsm.utils.plugins.module_utils.support.validator import Validator

class RoleManager(ABC):
    def __init__(
        self, 
        args: t.Mapping[str, t.Any] = {}, 
        vars: t.Mapping[str, t.Any] = {},
        module: t.Optional[ActionBase|LookupBase] = None
    ):
        self.meta: Fluent = Fluent()
        self.container: Fluent = Fluent()
        self.args: Fluent = Fluent()
        self.vars: Fluent = Fluent()
        self.cache: Fluent = Fluent()
        self.ret: Fluent = Fluent()

        self.modules: dict[str, t.Optional[ActionBase | LookupBase]] = {
            'action': None,
            'lookup': None,
        }

        if module:
            self.set_module(module)
    
        self.set_op(args, vars)

        if Kit.Validate().object_has_method(self, '_calback_post_init'):
            getattr(self, '_calback_post_init')()

    def set_op(self, args: t.Mapping[str, t.Any], vars: t.Mapping[str, t.Any]) -> None:
        op = args.get('op')
        if Kit.Validate().blank(op):
            raise ValueError('Operation argument op value cannot be blank')

        if Kit.Validate().object_has_method(self, '_calback_pre_op'):
            getattr(self, '_calback_pre_op')()
        
        schema = self._get_operation_validation_schema(args, vars)
        
        if Kit.Validate().filled(schema):
            args = Kit.Convert().to_primitive(args)
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

        role = Kit.Utils().class_get_primary_child(self, RoleManager)
        if not Kit.Validate().is_object(role):
            return
        
        role_name = role.__name__ #type: ignore
        role_name = Kit.Str().case_snake(str(role_name).strip()).strip().strip('_')
        self.meta.set('role.name', role_name)
    
    def _resolve_role_cfg(self, **kwargs)-> None:
        if self.meta.has('role.cfg'):
            return
        
        role_name = self.meta.get('role.name', '')
        if Kit.Validate().blank(role_name):
            return
        
        host = self.host()
        role_name = str(role_name).strip().strip('_').strip()
        self.meta.set('role.var.keys', Kit.Data().where(
            list(set(self.vars.keys() + list(self.host_vars(host, '', {}).keys()))),
            lambda entry: str(entry).startswith(f'{role_name}__'),
            default=[],
        ))

        for var_name in self.meta.get('role.var.keys', []):
            cfg_key = Kit.Str().chop_start(var_name, f'{role_name}__')
            self.meta.set(
                f'role.cfg.{cfg_key}',
                self.host_var_default(host, var_name)
            )
    
    def get_module(self)-> t.Optional[ActionBase|LookupBase]:
        for module_ in self.modules.keys():
            if self.modules[module_]:
                return self.modules[module_]
        
        return None

    def get_module_action(self) -> t.Optional[ActionBase]:
        module = self.get_module()
        return module if isinstance(module, ActionBase) else None

    def get_module_lookup(self) -> t.Optional[LookupBase]:
        module = self.get_module()
        return module if isinstance(module, LookupBase) else None

    def set_module(self, module: ActionBase|LookupBase):
        if isinstance(module, ActionBase):
            self.modules['action'] = module
        elif isinstance(module, LookupBase):
            self.modules['lookup'] = module

    def get_result(self):
        op_name = self.op('')
        if Kit.Validate().filled(op_name) and Kit.Validate().object_has_method(self, op_name):
            getattr(self, op_name)()

        self.cache.save()

        return {'result': self.ret.all()}
    
    def _template(self, data: t.Any, **kwargs)-> t.Any:
        if Kit.Validate().blank(data):
            return data

        if not self.get_module():
            raise RuntimeError('No module found to access templar')
        
        return Kit.Convert().from_ansible_template(self.get_module()._templar, data, **kwargs) #type: ignore

    def op(self, default: t.Any = '')-> t.Any:
        return self.args.get('op', default)

    def host(self, default: t.Any = None)-> t.Any:
        return self.vars.get('inventory_hostname', default)
    
    def inventory(self, **kwargs) -> list[str]:
        inventory = list(self.vars.get('groups.all', []))
        
        if kwargs.pop('remote', False) == True:
            inventory = Kit.Data().difference(inventory, ['vars'])

        return inventory

    def host_vars(self, host: str, key: str, default: t.Any = None) -> t.Any:
        return self.vars.get(Kit.Convert().to_data_key('hostvars', host, key), default)
    
    def host_ansible_facts(self, host: str, key: str, default: t.Any = None) -> t.Any:
        return self.vars.get(Kit.Convert().to_data_key('hostvars', host, 'ansible_facts', key), default)

    def domain(self, host: str = '')-> str:
        if Kit.Validate().blank(host):
            host = self.host()
        
        return self.host_var_default(host, '_domain', 'blrm')
    
    def host_var_default(self, host: str, key: str, default: t.Any = None) -> t.Any:
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

        return Kit.Validate().filled(Kit.Data().intersect(tags_run, list(set(list(args) + ['all'])))) and Kit.Validate().blank(Kit.Data().intersect(tags_skip, args))
    
    def is_op(self, op: str) -> bool:
        return self.op('op') == op
    
    def _exec_cmd(self, *args, **kwargs) -> CommandModel:
        module = self.get_module_action()
        if not module:
            raise RuntimeError('Action module not found to execute low level command')
        
        return Kit.Convert().as_command_model(
            module._low_level_execute_command(*args, **kwargs),
            list(args)[0] if Kit.Validate().filled(args) else kwargs.get('cmd')
        )
    
    def _exec_module(self, **kwargs):
        module = self.get_module_action()
        if not module:
            raise RuntimeError('Action module not found to execute module')
        
        kwargs = dict(kwargs)
        kwargs['task_vars'] = self.vars.all()

        return module._execute_module(**kwargs)
    
    # def _task_pipeline(self, )
    
    @abstractmethod
    def _get_operation_validation_schema(self, args: t.Mapping[str, t.Any], vars: t.Mapping[str, t.Any]) -> dict:
        pass