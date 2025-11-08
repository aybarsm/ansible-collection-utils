from __future__ import annotations
from ansible.module_utils.basic import AnsibleModule
import json

def is_str_blank(data: str)-> bool:
    return data.strip() == ''

def is_str_json(data: str)-> bool:
    data = str(data).strip()
    if is_str_blank(data):
        return False
    
    try:
        json.loads(data)
        return True
    except Exception as e:
        return False

def main():
    module = AnsibleModule(
        argument_spec={
            'method': {
                'required': True, 
                'type': 'str', 
                'choices': ['create', 'delete', 'get', 'ls', 'set', 'usage']
            },
            'endpoint': {
                'required': True, 
                'type': 'str'
            },
            'args': {
                'required': False, 
                'type': 'str',
                'default': '',
            }
        },
        supports_check_mode=False,
    )
    
    method = str(module.params['method'])
    endpoint = '/' + str(module.params['endpoint']).strip().strip('/')
    args = str(module.params['args']).strip()
    
    cmd = f'pvesh {method} {endpoint} --output-format=json'
    if args != '':
        cmd += f' {args}'

    [rc, stdout, stderr] = module.run_command(
        args=cmd,
        use_unsafe_shell=True
    )

    if rc != 0:
        module.fail_json(stderr)
    
    is_changed = method in ['create', 'set', 'delete']
    
    stdout = str(stdout).strip()
    result = None
    if not is_str_blank(stdout):
        if is_str_json(stdout):
            result = json.loads(stdout)
        else:
            for line in stdout.split('\n'):
                if is_str_json(line):
                    result = json.loads(line)
                    break
    
    if result == None:
        result = stdout

    module.exit_json(**{'changed': is_changed, 'result': result})

if __name__ == '__main__':
    main()