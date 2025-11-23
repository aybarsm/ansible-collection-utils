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
    return list(data) if isinstance(data, (list, set, tuple)) else [data]

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
        return to_safe_json(from_json(data))
    elif Validate.is_string(data) and Validate.str_is_yaml(data):
        return to_safe_json(from_yaml(data))
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

def from_qs(data: str, **kwargs) -> dict:
    from urllib.parse import parse_qs
    return parse_qs(data, **kwargs)

def to_querystring(data, keyAttr, valAttr=None, assignChar='=', joinChar='&', recurse=None, recurseIndentSteps=0, recurseIndentChar=' ', repeatJoinCharOnMainLevels=False):
    data = to_iterable(data)

    result = []

    def _to_querystring(innerData, level = 0):
        indent = recurseIndentChar * (level * recurseIndentSteps)
        for item in innerData:
            if keyAttr in item:
                if repeatJoinCharOnMainLevels and level == 0:
                    result.append('')
                if valAttr and valAttr in item:
                    result.append(f"{indent}{item[keyAttr]}{assignChar}{item[valAttr]}")
                else:
                    result.append(f"{indent}{item[keyAttr]}")

                if recurse and recurse in item and item[recurse]:
                    _to_querystring(item[recurse], level + 1)

    _to_querystring(data)

    return joinChar.join(result).strip(joinChar)

def to_list_of_dicts(data, defaults={}, *args, **kwargs):
    no_dot = kwargs.get('no_dot', False)
    combines = kwargs.pop('combine', [])
    combine_args = kwargs.pop('combine_args', {})
    data_keys = list(data.keys())
    ret = []

    for idx_item in range(0, len(data[data_keys[0]])):
        new_item = defaults.copy()

        if Validate.filled(combines) and Validate.filled(Data.get(combines, str(idx_item))):
            new_item = Data.combine(new_item, Data.get(combines, str(idx_item)), **combine_args)

        for data_key in data_keys:
            if no_dot:
                new_item[data_key] = data[data_key][idx_item]
            else:
                Data.set_(new_item, data_key, data[data_key][idx_item])

        ret.append(new_item)

    return ret

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

def from_cli(data, *args, **kwargs):
    data = to_string(data)
    as_iterable = kwargs.get('iterable', False)
    as_stripped = kwargs.get('stripped', False)
    
    ret = data.strip().strip('\'"')

    if Validate.str_is_json(data):
        return from_json(data)
    elif Validate.str_is_yaml(data):
        return from_yaml(data)
    elif as_iterable and Validate.contains(ret, ','):
        return [x for x in ','.split((ret if as_stripped else data)) if x]
    elif as_iterable:
        return to_iterable((ret if as_stripped else data))
    else:
        return to_iterable(ret if as_stripped else data) if as_iterable else (ret if as_stripped else data)

def from_ansible_template(templar, variable, **kwargs)-> T.Any:
    from ansible.template import is_trusted_as_template, trust_as_template
    extra_vars = kwargs.pop('extra_vars', {})
    remove_extra_vars = kwargs.pop('remove_extra_vars', True)

    if Validate.is_string(variable) and not is_trusted_as_template(variable):
        variable = trust_as_template(variable)
    
    for var_key, var_value in extra_vars.items():
        templar.available_variables[var_key] = var_value
    
    if Validate.is_iterable(variable):
        ret = Data.walk_values_deep(variable, lambda value_: templar.template(value_, **kwargs))
    else:
        ret = templar.template(variable, **kwargs)
    
    if not Validate.falsy(remove_extra_vars):
        for var_key, var_value in extra_vars.items():
            del templar.available_variables[var_key]
    
    return ret

def from_ansible(data: T.Any)-> T.Any:
    if Validate.is_mapping(data) or Validate.is_sequence(data):
        return from_yaml(to_native(data))
    
    return data

def to_items(
    data: T.Sequence[T.Any]|T.Mapping[T.Any, T.Any],
    key_name: str = 'key',
    value_name: str = 'value',
)-> list[dict[str, T.Any]]:
    iteratee = dict(data).items() if Validate.is_mapping(data) else enumerate(to_iterable(data))
    return [{key_name: key_, value_name: val_} for key_, val_ in iteratee]

def from_items(
    data: T.Sequence[T.Mapping[str, T.Any]],
    key_name: str = 'key',
    value_name: str = 'value',
    **kwargs,
)-> dict[str, T.Any]:
    default_key_prefix = kwargs.pop('default_key_prefix', 'unknown')
    default_value = kwargs.pop('default_value')
    default_key = f'{default_key_prefix}_{Factory.placeholder(mod='hashed')}'
    
    ret = {}
    for item in data:
        Data.set_(ret, Data.get(item, key_name, default_key), Data.get(item, value_name, default_value))

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

def as_ip_address(data: str, **kwargs)-> str:
    ph = Factory.placeholder(mod='hashed')
    default = kwargs.pop('default', ph)
    
    addr = Str.before(data, '/')
    proto = 'v4' if Validate.is_ip_v4(addr) else ('v6' if Validate.is_ip_v6(addr) else None)

    if Validate.blank(proto):
        return default if default != ph else data
            
    from_network = kwargs.pop('from_network', True)

    if not Validate.is_falsy(from_network):
        if Validate.is_ip_v4(addr) and Str.after_last(addr, '.') == '0':
            return Str.before_last(addr, '.') + '.1'
        elif Validate.is_ip_v6(addr):
            if addr.endswith('::'):
                return Str.before_last(addr, '::') + '::1'
            elif addr.endswith('::0'):
                return Str.before_last(addr, '::0') + '::1'
            elif addr.endswith(':0'):
                return Str.before_last(addr, ':0') + ':1'
            elif addr.endswith(':'):
                return Str.before_last(addr, ':') + ':1'
    
    return addr

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

def as_ip_merged_cidrs(value, action="merge"):
    import netaddr
    if not hasattr(value, "__iter__"):
        raise ValueError("cidr_merge: expected iterable, got " + repr(value))

    if action == "merge":
        try:
            return [str(ip) for ip in netaddr.cidr_merge(value)]
        except Exception as e:
            raise ValueError("cidr_merge: error in netaddr:\n%s" % e)

    elif action == "span":
        # spanning_cidr needs at least two values
        if len(value) == 0:
            return None
        elif len(value) == 1:
            try:
                return str(netaddr.IPNetwork(value[0]))
            except Exception as e:
                raise ValueError("cidr_merge: error in netaddr:\n%s" % e)
        else:
            try:
                return str(netaddr.spanning_cidr(value))
            except Exception as e:
                raise ValueError("cidr_merge: error in netaddr:\n%s" % e)
    elif action == "collapse":
        networks = list(set([netaddr.IPNetwork(ip) for ip in value]))
        ret = [
            net for net in networks
            if not any(
                (net != other) and (net.first >= other.first and net.last <= other.last)
                for other in networks
            )
        ]

        return [str(net_) for net_ in ret]

    else:
        raise ValueError("cidr_merge: invalid action '%s'" % action)
### END: Net

### BEGIN: Hash
def to_hash_scrypt(data: str, **kwargs)-> str:
    from passlib.hash import scrypt
    return scrypt.hash(data, **kwargs)
### END: Hash

### BEGIN: Json
def from_json(data: str, **kwargs)-> dict|list:
    import json
    return json.loads(data, **kwargs)

def to_json(
    data: T.Union[T.Sequence[T.Any], T.Mapping[T.Any, T.Any]], 
    **kwargs,
)-> str:
    import json
    return json.dumps(data, **kwargs)
### END: Json

### BEGIN: Yaml
def from_yaml(data: str)-> dict|list:
    import yaml
    return yaml.unsafe_load(data)

def to_yaml(
    data: T.Union[T.Sequence[T.Any], T.Mapping[T.Any, T.Any]], 
    **kwargs,
)-> str:
    import yaml
    return yaml.dump(data, **kwargs)
### END: Yaml

### BEGIN: Lua
def from_lua(data: str, **kwargs)-> dict|list:
    import luadata
    return luadata.unserialize(data, **kwargs)

def to_lua(data: T.Mapping|T.Sequence, **kwargs)-> str:
    import luadata
    return luadata.serialize(data, **kwargs)
### END: Lua

### BEGIN: Toml
def from_toml(data: str)-> dict|list:
    from tomlkit import parse
    return parse(data)

def to_toml(data: T.Mapping, **kwargs)-> str:
    from tomlkit import dumps
    return dumps(data, **kwargs)
### END: Toml

### BEGIN: Toml
def from_base64(data: T.Any, **kwargs)-> str|bytes:
    import base64
    decode_as = kwargs.pop('decode', 'utf-8')

    ret = base64.b64decode(to_text(data), **kwargs)

    if Validate.filled(decode_as):
        return ret.decode(decode_as)
    
    return ret

def to_base64(data: T.Any, **kwargs)-> str|bytes:
    import base64
    decode_as = kwargs.pop('decode', 'utf-8')
    encode_as = kwargs.pop('encode', 'utf-8')
    
    data = str(to_text(data))
    if Validate.filled(encode_as):
        data = data.encode(encode_as)
    
    ret = base64.b64encode(data, **kwargs)

    if Validate.filled(decode_as):
        return ret.decode(decode_as)

    return ret
### END: Toml

### BEGIN: Roles
def from_file_known_hosts(file_content: str)-> list[dict[str,str]]:
    import re
    ret = []

    for line in iter(str(file_content).splitlines()):
        normalised = re.sub(r'\s+', ' ', str(line).strip())
        segments = list(normalised.split(maxsplit=2))
        hash_ = str(Data.get(segments, '0', ''))
        type_ = str(Data.get(segments, '1', ''))
        key_ = str(Data.get(segments, '2', ''))

        if Validate.blank(hash_) or Validate.blank(type_) or Validate.blank(key_) or not type_.startswith('ssh-'):
            ret.append({'raw': line})
            continue

        if hash_.startswith('|1|'):
            hash_segments = list(Str.chop_start(hash_, '|1|').split(sep='|', maxsplit=2))
            hmac_key = str(Data.get(hash_segments, '0', ''))
            hmac_hash = str(Data.get(hash_segments, '1', ''))
            if Validate.blank(hmac_key) or Validate.blank(hmac_hash):
                raise ValueError(f'Unable to resolve known_hosts hash [{hash_}]')

            item = {
                'hmac_key': hmac_key,
                'hash': hmac_hash,
            }
        else:
            item = {
                'host': hash_
            }
        
        item['type'] = type_
        item['key'] = key_
        ret.append(item)
    
    return ret
### END: Roles