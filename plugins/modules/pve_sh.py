from __future__ import annotations
from ansible.module_utils.basic import AnsibleModule
import json
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

    module.exit_json(**{'data': json.loads(stdout)})

if __name__ == '__main__':
    main()