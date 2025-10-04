from __future__ import annotations
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.aybarsm.utils.plugins.module_utils.powerdns_api import PowerdnsApi, PdnsOperation

def main():
    pdns = PowerdnsApi(PdnsOperation.auth_zone)

    module_kwargs = pdns.get_ansible_module_arguments()
    module = AnsibleModule(**module_kwargs)

    ret = pdns.operation_execute(module)
    
    if 'failed' in ret and ret['failed'] == True:
        module.fail_json(ret['msg'], **ret['kwargs'])
    else:
        module.exit_json(**ret)

if __name__ == '__main__':
    main()