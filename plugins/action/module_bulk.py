from __future__ import annotations
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleActionFail
from ansible_collections.aybarsm.utils.plugins.module_utils.tools import Validator, Validate, Data, Helper

def _get_validation_schema()-> dict:
    return {
        'exec': {
            'type': 'dict',
            'required': True,
            'empty': False,
            'allow_unknown': True,
            'keysrules': {
                'type': 'string', 
                'regex': '^[a-z0-9_]+\\.[a-z0-9_]+\\.[a-z0-9_]+$',
            },
            'valuesrules': {
                'type': 'list',
                'required': True,
                'empty': False,
                'schema': {
                    'type': 'dict',
                    'required': True,
                    'empty': False,
                    'allow_unknown': True,
                },
            },
        },
        'async': {
            'type': 'boolean',
            'required': False,
            'default': False,
        }
    }

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars={}):
        task_args = Helper.yaml_parse(Helper.to_native(self._templar.template(self._task.args.copy())))
        
        v = Validator(_get_validation_schema()) # type: ignore
        if v.validate(task_args) != True: # type: ignore
            raise AnsibleActionFail(v.error_message()) # type: ignore
        
        task_args = v.normalized(task_args) # type: ignore
        
        ret = {}
        is_changed = False
        for module_, exec_ in task_args['exec'].items(): # type: ignore
            if module_ not in ret:
                ret[module_] = []

            for args_ in exec_:
                args_meta = Data.only_with(args_, meta=True)
                args_ = Data.all_except(args_, meta=True)

                result = self._execute_module(
                    module_name=module_,
                    module_args=args_,
                    task_vars=task_vars
                )

                if Validate.filled(args_meta):
                    invocation_args = Data.get(result, 'invocation.module_args', {})
                    Data.set(result, 'invocation.module_args', Data.combine(args_meta, invocation_args, recursive=True))

                ret[module_].append(result)
                is_changed = Validate.truthy(Data.get(result, 'changed'))

                if Validate.truthy(Data.get(result, 'failed')):
                    raise AnsibleActionFail(f'[{module_}]: {Data.get(result, 'msg', '')}')
        
        return {'changed': is_changed, 'result': ret}
