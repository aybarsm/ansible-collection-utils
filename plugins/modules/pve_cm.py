from __future__ import annotations
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.aybarsm.utils.plugins.module_utils.tools_safe import Validate
import re

_MODULE_ARGUMENTS = {
    'supports_check_mode': False,
    'argument_spec': {
        'method': {
            'required': True, 
            'type': 'str', 
            'choices': [
                'qdevice', 
                'addnode', 
                'apiver', 
                'create', 
                'delnode', 
                'add', 
                'expected',
                'keygen', 
                'mtunnel', 
                'nodes', 
                'status', 
                'updatecerts'
            ],
        },
        'args': {
            'required': False, 
            'type': 'str',
            'default': '',
        },
        'no_exception': {
            'required': False, 
            'type': 'bool',
            'default': False,
        },
        'lines': {
            'required': False, 
            'type': 'bool',
            'default': False,
        },
        'clean_lines': {
            'required': False, 
            'type': 'bool',
            'default': False,
        },
    },
}

def main():
    module = AnsibleModule(**_MODULE_ARGUMENTS)
    
    method = str(module.params.get('method', ''))
    args = str(module.params.get('args', '')).strip()
    no_exception = module.params.get('no_exception', False)
    lines = module.params.get('lines', False)
    clean_lines = module.params.get('clean_lines', False)
    
    cmd = f'pvecm {method}'
    if args != '':
        cmd += f' {args}'

    [rc, stdout, stderr] = module.run_command(
        args=cmd,
        use_unsafe_shell=True
    )
    
    rc = int(rc)
    stdout = str(stdout)
    stderr = str(stderr)
    
    ret = {
        'changed': method in ['qdevice', 'addnode', 'create', 'delnode', 'add', 'mtunnel', 'updatecerts'],
        'rc': rc,
        'stderr': stderr,
        'stderr_lines': stderr.splitlines(),
        'stdout': stdout,
        'stdout_lines': stdout.splitlines(),
    }

    if lines or clean_lines:
        ret_lines = list(ret.get('stderr_lines', []) + ret.get('stdout_lines', []))
        if clean_lines:
            ret_lines = map(
                lambda entry: re.sub(r'\s+', ' ', str(entry).strip()),
                ret_lines
            )
            
            ret['lines'] = []

            for line_ in ret_lines:
                if Validate_filled(line_):
                    ret['lines'].append(line_)
        else:
            ret['lines'] = ret_lines

    is_failed = rc != 0
    if is_failed and no_exception != True:
        module.fail_json(stderr)

    module.exit_json(**ret)

if __name__ == '__main__':
    main()