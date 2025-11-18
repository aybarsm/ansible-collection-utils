import typing as T
import datetime
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    __ansible, __data, __factory, __str, __utils, __validate, __ipaddress, __hashlib
)

Ansible = __ansible()
Data = __data()
Factory = __factory()
Str = __str()
Utils = __utils()
Validate = __validate()

def to_pydash(data: T.Union[T.Sequence[T.Any], T.Mapping[T.Any, T.Any]])-> dict|list:
    if Validate.is_sequence(data):
        return list(data)
    else:
        return dict(data)

def to_md5(data: T.Any)-> str:
    return __hashlib().md5(str(to_text(data)).encode()).hexdigest()

def as_ts_mod(ts: datetime.datetime, mod: str)-> str|int:
    mod = mod.lower()

    if mod in ['string', 'str']:
        return str(ts.strftime("%Y-%m-%dT%H:%M:%SZ"))
    elif mod in ['safe']:
        return str(ts.strftime("%Y%m%dT%H%M%SZ"))
    elif mod in ['long']:
        return str(ts.strftime("%Y-%m-%dT%H:%M:%S") + f".{ts.microsecond * 1000:09d}Z")
    elif mod in ['long_safe']:
        return str(ts.strftime("%Y%m%dT%H%M%S") + f".{ts.microsecond * 1000:09d}Z")
    elif mod in ['timestamp', 'ts']:
        return int(ts.timestamp())
    elif mod in ['asn1']:
        return str(ts.strftime('%Y%m%d%H%M%SZ'))
    else:
        raise ValueError(f'Unknown TS mod [{mod}]')

def to_iterable(data)-> list:
    return list(data) if Validate.is_sequence(data) else [data]

def as_copied(data):
    import copy

    try:
        return copy.deepcopy(data)
    except Exception:
        pass
    
    try:
        return copy.copy(data)
    except Exception:
        pass
    
    return data

def from_mapping_to_callable(data: T.Mapping[str, T.Any], **kwargs)-> T.Callable:
    no_dot = kwargs.pop('no_dot', False)
    
    if no_dot:
        return lambda entry: all([key in entry and entry[key] == val for key, val in data.items()])
    else:
        return lambda entry: all([Data.has(entry, key) and Data.get(entry, key) == val for key, val in data.items()])

def to_data_key(*args: str, **kwargs)-> str:
    import re
    include_blanks = Validate.truthy(kwargs.pop('blanks', False))
    ret = []
    
    for key in args:
        key = re.sub(r'\.+', '.', key).strip('.')
        if include_blanks or Validate.filled(key):
            ret.append(key)
    
    return '.'.join(ret)

def to_safe_json(data):
    if Validate.is_bytes(data):
        return to_safe_json(to_text(data))
    elif Validate.is_string(data) and Validate.str_is_json(data):
        return to_safe_json(Utils.json_parse(data))
    elif Validate.is_string(data) and Validate.str_is_yaml(data):
        return to_safe_json(Utils.yaml_parse(data))
    elif isinstance(data, (str, int, float, bool)) or data is None:
        return data
    elif Validate.is_ansible_mapping(data):
        return to_safe_json(to_text(data))
    elif isinstance(data, dict):
        return {str(k): to_safe_json(v) for k, v in data.items()}
    elif isinstance(data, (list, tuple)):
        return [to_safe_json(item) for item in data]
    elif hasattr(data, '__str__'):
        try:
            return str(data)
        except Exception:
            return "<unserializable object>"

    # Fallback
    return f"<unsupported type: {type(data)}>"

def to_url_encode(data: T.Mapping[str, T.Any], **kwargs)-> str:
    import urllib.parse
    
    data = dict(data)
    for key in list(data.keys()):
        if Validate.is_bool(data[key]):
            data[key] = 'true' if data[key] else 'false'
    
    return urllib.parse.urlencode(data, **kwargs)

### BEGIN: Ansible
def to_text(*args, **kwargs)-> str:
    from ansible.module_utils.common.text.converters import to_text
    strip_quotes = kwargs.pop('strip_quotes', False)

    ret = to_text(*args, **kwargs)
    
    if strip_quotes:
        ret = str(ret).strip().strip("'").strip().strip('"').strip()

    return ret

def to_native(*args, **kwargs)-> str:
    return to_text(*args, **kwargs)

def to_string(*args, **kwargs)-> str:
    return to_text(*args, **kwargs)

def to_bytes(*args, **kwargs):
    from ansible.module_utils.common.text.converters import to_bytes
    return to_bytes(*args, **kwargs)

def from_ansible_template(templar, variable, **kwargs)-> T.Any:
    from ansible.template import is_trusted_as_template, trust_as_template 
    extra_vars = kwargs.pop('extra_vars', {})
    remove_extra_vars = kwargs.pop('remove_extra_vars', True)

    if Validate.is_string(variable) and not is_trusted_as_template(variable):
        variable = trust_as_template(variable)
    
    for var_key, var_value in extra_vars.items():
        templar.available_variables[var_key] = var_value
    
    ret = templar.template(variable, **kwargs)
    
    if not Validate.falsy(remove_extra_vars):
        for var_key, var_value in extra_vars.items():
            del templar.available_variables[var_key]
    
    return ret
### END: Ansible

### BEGIN: Type
def to_type_name(data: T.Any)-> str:
    return type(data).__name__

def to_type_module(data: T.Any)-> str:
    return type(data).__name__
### END: Type

### BEGIN: Net
def to_ip_address(data, **kwargs):
    ph = Factory.placeholder(mod='hashed')
    default = kwargs.get('default', ph)

    try:
        return __ipaddress().ip_address(data)
    except Exception as e:
        if default == ph:
            raise e
        
        return default
    
def to_ip_network(data, **kwargs):
    ph = Factory.placeholder(mod='hashed')
    default = kwargs.get('default', ph)

    try:
        return __ipaddress().ip_network(data)
    except Exception as e:
        if default == ph:
            raise e
        
        return default

def as_ip_segments(data: str)-> dict:
    type_ = Ansible.utils_ipaddr(data, 'type')
    type_ = 'addr' if type_ == 'address' else ('net' if type_ == 'network' else None)
    
    net = Ansible.utils_ipaddr(data, 'network/prefix')
    if net and data == net:
        cidr = net
        addr = Str.before(cidr, '/')
        addr_net = addr
    else:
        cidr = Ansible.utils_ipaddr(data, 'address/prefix')
        addr = Ansible.utils_ipaddr(data, 'address')
        addr_net = Ansible.utils_ipaddr(net, 'address') if net else None

    v4 = Ansible.utils_ipaddr(data, 'ipv4')
    v6 = Ansible.utils_ipaddr(data, 'ipv6')
    proto = 'v6' if v6 in [data, cidr, addr] else ('v4' if v4 in [data, cidr, addr] else None)

    pub = Ansible.utils_ipaddr(addr, 'public') if addr else None
    pri = Ansible.utils_ipaddr(addr, 'private') if addr else None

    size_net = Ansible.utils_ipaddr(net, 'size') if net else None
    host_cidr = Ansible.utils_ipaddr(data, 'host/prefix')
    return {
        'raw': data,
        'type': type_,
        'addr': addr,
        'cidr': cidr,
        'prefix': Ansible.utils_ipaddr(data, 'prefix'),
        'proto': proto,
        'ctrl': {
            'v4': proto == 'v4',
            'v6': proto == 'v6',
            'pub': pub in [data, cidr, addr],
            'pri': pri in [data, cidr, addr],
            'valid': Validate.filled(type_) and Validate.filled(proto),
        },
        'net': {
            'addr': addr_net,
            'cidr': net,
            # 'subnet': Ansible.utils_ipaddr(net, 'subnet') if net else None,
            'size': size_net,
            'mask': Ansible.utils_ipaddr(net, 'netmask') if net else None,
            'broadcast': Ansible.utils_ipaddr(net, 'broadcast') if net else None,
        },
        'host': {
            'addr': Ansible.utils_ipaddr(host_cidr, 'address') if host_cidr else None,
            'cidr': host_cidr,
        },
        'wrap': {
            'addr': Ansible.utils_ipaddr(addr, 'wrap') if addr else None,
            'cidr': Ansible.utils_ipaddr(cidr, 'wrap') if cidr else None,
        },
        'first': {
            'addr': Ansible.utils_ipaddr(Ansible.utils_ipaddr(net, '1'), 'address') if net else None,
            'cidr': Ansible.utils_ipaddr(net, '1') if net else None,
            'usable': Ansible.utils_ipaddr(net, 'first_usable') if net else None,
        },
        'last': {
            'addr': Ansible.utils_ipaddr(Ansible.utils_ipaddr(net, '-1'), 'address') if net else None,
            'cidr': Ansible.utils_ipaddr(net, '-1') if net else None,
            'usable': Ansible.utils_ipaddr(net, 'last_usable') if net else None,
        },
        'range': {
            'usable': str(Ansible.utils_ipaddr(net, 'range_usable')).split('-', 2) if net and size_net and size_net > 1 else None,
        }
    }

def as_ip_segments_validated(data, on_invalid: T.Optional[T.Callable] = None, **kwargs)-> list:
    ret = Data.map(to_iterable(data), lambda ip_: as_ip_segments(ip_))

    if Validate.filled(ret) and Validate.filled(on_invalid):
        for idx, item in enumerate(ret):
            if Data.get(item, 'ctrl.valid') == True:
                continue
            
            if on_invalid:
                e = Utils.call(on_invalid, item, idx)
                if Validate.is_exception(e):
                    raise e
        
    return list(ret)
### END: Net