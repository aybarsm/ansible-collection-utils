### BEGIN: Utils
def utils_ipaddr(value, query: str = ''):
    from ansible_collections.ansible.utils.plugins.plugin_utils.base.ipaddr_utils import ipaddr
    return ipaddr(value, query)
### END: Utils