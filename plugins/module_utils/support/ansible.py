### BEGIN: Imports
from ansible_collections.aybarsm.utils.plugins.module_utils.support.definitions import (
    t, 
)
### END: Imports
### BEGIN: ImportManager
### END: ImportManager

### BEGIN: Misc
def Ansible_display(*args, **kwargs) -> t.Any:
    from ansible.utils.display import Display
    return Display(*args, **kwargs)
### END: Misc

### BEGIN: Filter
def Ansible_filter_map(*args, **kwargs) -> t.Any:
    from ansible.plugins.filter.core import wrapped_map
    return wrapped_map(*args, **kwargs)

def Ansible_filter_select(*args, **kwargs) -> t.Any:
    from ansible.plugins.filter.core import wrapped_select
    return wrapped_select(*args, **kwargs)

def Ansible_filter_reject(*args, **kwargs) -> t.Any:
    from ansible.plugins.filter.core import wrapped_reject
    return wrapped_reject(*args, **kwargs)

def Ansible_filter_selectattr(*args, **kwargs) -> t.Any:
    from ansible.plugins.filter.core import wrapped_selectattr
    return wrapped_selectattr(*args, **kwargs)

def Ansible_filter_rejectattr(*args, **kwargs) -> t.Any:
    from ansible.plugins.filter.core import wrapped_rejectattr
    return wrapped_rejectattr(*args, **kwargs)
### END: Filter

### BEGIN: Template
def Ansible_is_trusted_as_template(*args, **kwargs) -> t.Any:
    from ansible.template import is_trusted_as_template
    return Ansible_is_trusted_as_template(*args, **kwargs)

def Ansible_trust_as_template(*args, **kwargs) -> t.Any:
    from ansible.template import trust_as_template
    return Ansible_trust_as_template(*args, **kwargs)
### END: Template

### BEGIN: Utils
def Ansible_utils_ipaddr(value, query: str = ''):
    from ansible_collections.ansible.utils.plugins.plugin_utils.base.ipaddr_utils import ipaddr
    return ipaddr(value, query)
### END: Utils