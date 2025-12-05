import typing as t
### BEGIN: ImportManager
### END: ImportManager

### BEGIN: Misc
def display(*args, **kwargs) -> t.Any:
    from ansible.utils.display import Display
    return Display(*args, **kwargs)
### END: Misc

### BEGIN: Filter
def filter_map(*args, **kwargs) -> t.Any:
    from ansible.plugins.filter.core import wrapped_map
    return wrapped_map(*args, **kwargs)

def filter_select(*args, **kwargs) -> t.Any:
    from ansible.plugins.filter.core import wrapped_select
    return wrapped_select(*args, **kwargs)

def filter_reject(*args, **kwargs) -> t.Any:
    from ansible.plugins.filter.core import wrapped_reject
    return wrapped_reject(*args, **kwargs)

def filter_selectattr(*args, **kwargs) -> t.Any:
    from ansible.plugins.filter.core import wrapped_selectattr
    return wrapped_selectattr(*args, **kwargs)

def filter_rejectattr(*args, **kwargs) -> t.Any:
    from ansible.plugins.filter.core import wrapped_rejectattr
    return wrapped_rejectattr(*args, **kwargs)
### END: Filter

### BEGIN: Template
def is_trusted_as_template(*args, **kwargs) -> t.Any:
    from ansible.template import is_trusted_as_template
    return is_trusted_as_template(*args, **kwargs)

def trust_as_template(*args, **kwargs) -> t.Any:
    from ansible.template import trust_as_template
    return trust_as_template(*args, **kwargs)
### END: Template

### BEGIN: Utils
def utils_ipaddr(value, query: str = ''):
    from ansible_collections.ansible.utils.plugins.plugin_utils.base.ipaddr_utils import ipaddr
    return ipaddr(value, query)
### END: Utils