import typing as t

### BEGIN: Utils
def utils_ipaddr(value, query: str = ''):
    from ansible_collections.ansible.utils.plugins.plugin_utils.base.ipaddr_utils import ipaddr
    return ipaddr(value, query)

def filter_map(*args, **kwargs) -> t.Any:
    from ansible.plugins.filter.core import wrapped_map
    return wrapped_map(*args, **kwargs)

def filter_select(*args, **kwargs) -> t.Any:
    from ansible.plugins.filter.core import wrapped_select
    return wrapped_select(*args, **kwargs)

def filter_reject(*args, **kwargs) -> t.Any:
    from ansible.plugins.filter.core import wrapped_reject, wrapped_selectattr, wrapped_rejectattr
    return wrapped_reject(*args, **kwargs)

def filter_selectattr(*args, **kwargs) -> t.Any:
    from ansible.plugins.filter.core import wrapped_selectattr, wrapped_rejectattr
    return wrapped_selectattr(*args, **kwargs)

def filter_rejectattr(*args, **kwargs) -> t.Any:
    from ansible.plugins.filter.core import wrapped_rejectattr
    return wrapped_rejectattr(*args, **kwargs)
### END: Utils