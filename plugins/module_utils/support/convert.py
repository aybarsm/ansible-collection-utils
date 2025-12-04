import typing as t
import types as tt
import datetime, inspect, uuid, hashlib, ipaddress, inspect, copy, re, netaddr
from ansible_collections.aybarsm.utils.plugins.module_utils.support.types import (
    ENUMERATABLE, CallableParameterTypeMap, CallableParameterKind, PositiveInt
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.definitions import (
    CommandModel, Sentinel
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.ansible import (
    utils_ipaddr as Ansible_utils_ipaddr,
    is_trusted_as_template as Ansible_is_trusted_as_template,
    trust_as_template as Ansible_trust_as_template,
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.data import (
    get as Data_get,
    has as Data_has,
    set_ as Data_set,
    combine as Data_combine,
    map as Data_map,
    walk_values_deep as Data_walk_values_deep,
    where as Data_where,
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.factory import (
    ts as Factory_ts, 
    random_string as Factory_random_string,
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.str import (
    finish as Str_finish,
    before as Str_before,
    before_last as Str_before_last,
    after_last as Str_after_last,
    chop_start as Str_chop_start,
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.utils import (
    call as Utils_call,
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.validate import (
    truthy as Validate_truthy,
    falsy as Validate_falsy,
    blank as Validate_blank, 
    filled as Validate_filled,
    is_mapping as Validate_is_mapping,
    is_bytes as Validate_is_bytes,
    is_bool as Validate_is_bool,
    is_string as Validate_is_string,
    str_is_json as Validate_str_is_json,
    str_is_yaml as Validate_str_is_yaml,
    is_ansible_mapping as Validate_is_ansible_mapping,
    is_hashable as Validate_is_hashable,
    contains as Validate_contains,
    is_iterable as Validate_is_iterable,
    is_enumeratable as Validate_is_enumeratable,
    is_sequence as Validate_is_sequence,
    is_type_python_native as Validate_is_type_python_native,
    is_ip_v4 as Validate_is_ip_v4,
    is_ip_v6 as Validate_is_ip_v6,
    is_exception as Validate_is_exception,
    callable_parameter_is_kind as Validate_callable_parameter_is_kind,
    callable_parameter_has as Validate_callable_parameter_has,
)

def as_id(
    data: t.Any, 
    prefix: str = '', 
    suffix: str = '', 
    use_ts: bool = True, 
    as_hash: bool = True,
    random_string: t.Optional[PositiveInt] = None,
) -> str:
    ret = [str(id(data))]
    
    if use_ts:
        ret.append(str(Factory_ts(mod='long')))
    
    if random_string:
        ret.append(Factory_random_string(random_string))
    
    ret = f'{prefix}{'_'.join(ret)}{suffix}'

    if as_hash:
        return to_md5(ret)
    else:
        return ret

def to_pydash(data: t.Iterable[t.Any])-> dict | list:
    if Validate_is_mapping(data):
        return dict(data)
    else:
        return list(data)

def to_md5(data: t.Any)-> str:
    return hashlib.md5(str(to_text(data)).encode()).hexdigest()

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

def to_enumeratable(data: t.Any) -> list:
    if Validate_is_mapping(data):
        return list(dict(data).values())
    
    return list(data) if isinstance(data, (list, set, tuple)) else [data]

def as_copied(data):
    try:
        return copy.deepcopy(data)
    except Exception:
        pass
    
    try:
        return copy.copy(data)
    except Exception:
        pass
    
    return data

def from_mapping_to_callable(data: t.Mapping[str, t.Any], **kwargs)-> t.Callable:
    no_dot = kwargs.pop('no_dot', False)
    
    if no_dot:
        return lambda entry: all([key in entry and entry[key] == val for key, val in data.items()])
    else:
        return lambda entry: all([Data_has(entry, key) and Data_get(entry, key) == val for key, val in data.items()])

def to_data_key(*args: str, **kwargs)-> str:
    include_blanks = Validate_truthy(kwargs.pop('blanks', False))
    ret = []
    
    for key in args:
        key = re.sub(r'\.+', '.', key).strip('.')
        if include_blanks or Validate_filled(key):
            ret.append(key)
    
    return '.'.join(ret)

def to_safe_json(data):
    if Validate_is_bytes(data):
        return to_safe_json(to_text(data))
    elif Validate_is_string(data) and Validate_str_is_json(data):
        return to_safe_json(from_json(data))
    elif Validate_is_string(data) and Validate_str_is_yaml(data):
        return to_safe_json(from_yaml(data))
    elif isinstance(data, (str, int, float, bool)) or data is None:
        return data
    elif Validate_is_ansible_mapping(data):
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

def to_url_encode(data: t.Mapping[str, t.Any], **kwargs)-> str:
    import urllib.parse
    
    data = dict(data)
    for key in list(data.keys()):
        if Validate_is_bool(data[key]):
            data[key] = 'true' if data[key] else 'false'
    
    return urllib.parse.urlencode(data, **kwargs)

def from_querystring(data: str, **kwargs) -> dict:
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

        if Validate_filled(combines) and Validate_filled(Data_get(combines, str(idx_item))):
            new_item = Data_combine(new_item, Data_get(combines, str(idx_item)), **combine_args)

        for data_key in data_keys:
            if no_dot:
                new_item[data_key] = data[data_key][idx_item]
            else:
                Data_set(new_item, data_key, data[data_key][idx_item])

        ret.append(new_item)

    return ret

def as_hash(
    key: int,
    value: t.Any, 
    by: t.Optional[t.Union[t.Literal[True], str, ENUMERATABLE[str], t.Callable]] = None,
) -> str:
    if isinstance(by, t.Callable):
        return str(Utils_call(by, value, key))

    if by == True or by == None or Validate_blank(by):
        if Validate_is_hashable(value):
            return str(hash(value))
        else:
            raise RuntimeError(f'Unhashable item type [{type(value).__name__}]')
    
    if isinstance(by, str) and Validate_filled(by):
        by = [by]

    if isinstance(value, t.Mapping) or isinstance(value, object):
        return to_md5('|'.join([to_text(Data_get(value, key_, Sentinel.hash)) for key_ in by])) #type: ignore
    
    raise RuntimeError(f'Unhashable condition for item type [{type(value).__name__}]')

def as_concurrent_command(commands: ENUMERATABLE[str]) -> str:
    tmp_prefix = f'ansible.cmd_{Sentinel.hash}'
    ret = {
        'cmd': [],
        'wait': [],
        'structure': [],
        'output': [],
    }

    for idx, cmd in enumerate(commands):
        cmd_seq = str(idx + 1)
        path_out = f'/tmp/{tmp_prefix}.{cmd_seq}.out'
        path_err = f'/tmp/{tmp_prefix}.{cmd_seq}.err'
        
        ret['cmd'].append(' '.join([
            str(cmd).strip(),
            f'>{path_out}',
            f'2>{path_err}',
            '&',
            f'pid{cmd_seq}=$!',
        ]))

        ret['wait'].extend([
            f'wait "$pid1"', 
            f'rc{cmd_seq}=$?',
        ])

        ret['structure'].extend([
            f"out{cmd_seq}=$(cat {path_out} | sed 's/\"/\\\\\"/g')",
            f"err{cmd_seq}=$(cat {path_err} | sed 's/\"/\\\\\"/g')",
        ])

        output = [
            f'"cmd": {cmd_seq}',
            f'"pid": $pid{cmd_seq}',
            f'"rc": $rc{cmd_seq}',
            f'"out": \\"$out{cmd_seq}\\"',
            f'"err": \\"$err{cmd_seq}\\"',
        ]
        ret['output'].append('{' + ', '.join(output) + '}')
    
    return ''.join([
        '(',
        Str_finish('; '.join(ret['cmd']), '; '),
        Str_finish('; '.join(ret['wait']), '; '),
        Str_finish('; '.join(ret['structure']), '; '),
        'printf "[',
        ', '.join(ret['output']),
        Str_finish(']"', '; '),
        Str_finish(f'rm /tmp/{tmp_prefix}*', '; '),
        ')',
    ])

def as_lines(data: t.Optional[str]) -> list[str]:
    if not data or Validate_blank(data):
        return []

    return str(data).splitlines()

def as_cleaned_lines(data: t.Optional[str]) -> list[str]:
    if not data or Validate_blank(data):
        return []
    
    return [line for line in Data_map(
            as_lines(data),
            lambda entry: re.sub(r'\s+', ' ', str(entry).strip())
        ) if Validate_filled(line)]

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

def to_primitive(*args, **kwargs) -> t.Any:
    ret = to_text(*args, **kwargs)
    if Validate_str_is_yaml(ret):
        ret = from_yaml(ret)
        if Validate_is_mapping(ret):
            return dict(ret)
        else:
            return list(ret)
    else:
        return ret

def to_bytes(*args, **kwargs):
    from ansible.module_utils.common.text.converters import to_bytes
    return to_bytes(*args, **kwargs)

def from_cli(data, *args, **kwargs):
    data = to_string(data)
    as_iterable = kwargs.get('iterable', False)
    as_stripped = kwargs.get('stripped', False)
    
    ret = data.strip().strip('\'"')

    if Validate_str_is_json(data):
        return from_json(data)
    elif Validate_str_is_yaml(data):
        return from_yaml(data)
    elif as_iterable and Validate_contains(ret, ','):
        return [x for x in ','.split((ret if as_stripped else data)) if x]
    elif as_iterable:
        return to_iterable((ret if as_stripped else data))
    else:
        return to_iterable(ret if as_stripped else data) if as_iterable else (ret if as_stripped else data)

def __from_ansible_template(templar, variable, **kwargs) -> t.Any:
    if Validate_is_string(variable) and not Ansible_is_trusted_as_template(variable):
        variable = Ansible_trust_as_template(variable)
    
    variable = templar.template(variable, **kwargs)
    
    if Validate_is_mapping(variable):
        return dict(variable)
    elif Validate_is_enumeratable(variable):
        return to_iterable(variable)
    else:
        return variable

def from_ansible_template(templar, variable, **kwargs)-> t.Any:
    extra_vars = kwargs.pop('extra_vars', {})
    remove_extra_vars = kwargs.pop('remove_extra_vars', True)
    
    for var_key, var_value in extra_vars.items():
        templar.available_variables[var_key] = var_value
    
    if Validate_is_iterable(variable):
        variable = Data_walk_values_deep(variable, lambda value_: __from_ansible_template(templar, value_, **kwargs))
    else:
        variable = __from_ansible_template(templar, variable, **kwargs)
    
    if not Validate_falsy(remove_extra_vars):
        for var_key, var_value in extra_vars.items():
            del templar.available_variables[var_key]
    
    if Validate_is_mapping(variable):
        return dict(variable)
    elif Validate_is_enumeratable(variable):
        return to_iterable(variable)
    else:
        return variable

def from_ansible(data: t.Any)-> t.Any:
    if Validate_is_mapping(data) or Validate_is_sequence(data):
        return from_yaml(to_native(data))
    
    return data

def to_items(
    data: t.Iterable[t.Any],
    key_name: str = 'key',
    value_name: str = 'value',
)-> list[dict[str, t.Any]]:
    iteratee = dict(data).items() if Validate_is_mapping(data) else enumerate(to_iterable(data))
    return [{key_name: key_, value_name: val_} for key_, val_ in iteratee]

def from_items(
    data: t.Sequence[t.Mapping[str, t.Any]],
    key_name: str = 'key',
    value_name: str = 'value',
    **kwargs,
)-> dict[str, t.Any]:
    default_key_prefix = kwargs.pop('default_key_prefix', 'unknown')
    default_value = kwargs.pop('default_value')
    default_key = f'{default_key_prefix}_{Sentinel.hash}'
    
    ret = {}
    for item in data:
        Data_set(ret, Data_get(item, key_name, default_key), Data_get(item, value_name, default_value))

    return ret

def as_command_model(data: t.Mapping[str, t.Any], command: t.Optional[str] = None) -> CommandModel:
    data = dict(data)
    data['stdout'] = to_text(data['stdout']).strip()
    data['stderr'] = to_text(data['stderr']).strip()

    ret = {
        'rc': int(to_text(data['rc'])),
        'out': data['stdout'] if Validate_filled(data['stdout']) else None,
        'err': data['stderr'] if Validate_filled(data['stderr']) else None,
        'command': command,
    }
    
    return CommandModel(**ret)
### END: Ansible

### BEGIN: Type
def to_type_name(data: t.Any) -> str:
    return type(data).__name__

def to_type_module(data: t.Any) -> str:
    return type(data).__module__

def as_non_native_types(data: t.Union[t.Any, ENUMERATABLE[t.Any]])-> tuple[t.Any, ...]:
    return tuple([item for item in to_iterable(data) if not Validate_is_type_python_native(item)])

def as_type_module_mapping(data: t.Union[t.Any, ENUMERATABLE[t.Any]]) -> list[t.Any]:
    ret = []

    for item in to_iterable(data):
        ret_item = {
            'item': item,
            'module': None,
            'src_file': None,
            'validate': Validate_is_type_python_native(item),
        }
        
        try:
            ret_item['module'] = item.__module__
        except Exception:
            pass

        try:
            ret_item['src_file'] = inspect.getsourcefile(item)
        except TypeError:
            pass

        ret.append(ret_item)

    return ret
### END: Type

### BEGIN: Net
def to_ip_address(data: t.Any, **kwargs):
    default = kwargs.get('default', Sentinel.hash)

    try:
        return ipaddress.ip_address(to_text(data))
    except Exception as e:
        if default == Sentinel.hash:
            raise e
        
        return default
    
def to_ip_network(data: t.Any, **kwargs):
    default = kwargs.get('default', Sentinel.hash)

    try:
        return ipaddress.ip_network(to_text(data))
    except Exception as e:
        if default == Sentinel.hash:
            raise e
        
        return default

def as_ip_address(data: str, **kwargs)-> str:
    default = kwargs.pop('default', Sentinel.hash)
    
    addr = Str_before(data, '/')
    proto = 'v4' if Validate_is_ip_v4(addr) else ('v6' if Validate_is_ip_v6(addr) else None)

    if Validate_blank(proto):
        return default if default != Sentinel.hash else data
            
    from_network = kwargs.pop('from_network', True)

    if not Validate_falsy(from_network):
        if Validate_is_ip_v4(addr) and Str_after_last(addr, '.') == '0':
            return Str_before_last(addr, '.') + '.1'
        elif Validate_is_ip_v6(addr):
            if addr.endswith('::'):
                return Str_before_last(addr, '::') + '::1'
            elif addr.endswith('::0'):
                return Str_before_last(addr, '::0') + '::1'
            elif addr.endswith(':0'):
                return Str_before_last(addr, ':0') + ':1'
            elif addr.endswith(':'):
                return Str_before_last(addr, ':') + ':1'
    
    return addr

def as_ip_segments(data: str)-> dict:
    type_ = Ansible_utils_ipaddr(data, 'type')
    type_ = 'addr' if type_ == 'address' else ('net' if type_ == 'network' else None)
    
    net = Ansible_utils_ipaddr(data, 'network/prefix')
    if net and data == net:
        cidr = net
        addr = Str_before(cidr, '/')
        addr_net = addr
    else:
        cidr = Ansible_utils_ipaddr(data, 'address/prefix')
        addr = Ansible_utils_ipaddr(data, 'address')
        addr_net = Ansible_utils_ipaddr(net, 'address') if net else None

    v4 = Ansible_utils_ipaddr(data, 'ipv4')
    v6 = Ansible_utils_ipaddr(data, 'ipv6')
    proto = 'v6' if v6 in [data, cidr, addr] else ('v4' if v4 in [data, cidr, addr] else None)

    pub = Ansible_utils_ipaddr(addr, 'public') if addr else None
    pri = Ansible_utils_ipaddr(addr, 'private') if addr else None

    size_net = Ansible_utils_ipaddr(net, 'size') if net else None
    host_cidr = Ansible_utils_ipaddr(data, 'host/prefix')
    return {
        'raw': data,
        'type': type_,
        'addr': addr,
        'cidr': cidr,
        'prefix': Ansible_utils_ipaddr(data, 'prefix'),
        'proto': proto,
        'ctrl': {
            'v4': proto == 'v4',
            'v6': proto == 'v6',
            'pub': pub in [data, cidr, addr],
            'pri': pri in [data, cidr, addr],
            'valid': Validate_filled(type_) and Validate_filled(proto),
        },
        'net': {
            'addr': addr_net,
            'cidr': net,
            # 'subnet': Ansible_utils_ipaddr(net, 'subnet') if net else None,
            'size': size_net,
            'mask': Ansible_utils_ipaddr(net, 'netmask') if net else None,
            'broadcast': Ansible_utils_ipaddr(net, 'broadcast') if net else None,
        },
        'host': {
            'addr': Ansible_utils_ipaddr(host_cidr, 'address') if host_cidr else None,
            'cidr': host_cidr,
        },
        'wrap': {
            'addr': Ansible_utils_ipaddr(addr, 'wrap') if addr else None,
            'cidr': Ansible_utils_ipaddr(cidr, 'wrap') if cidr else None,
        },
        'first': {
            'addr': Ansible_utils_ipaddr(Ansible_utils_ipaddr(net, '1'), 'address') if net else None,
            'cidr': Ansible_utils_ipaddr(net, '1') if net else None,
            'usable': Ansible_utils_ipaddr(net, 'first_usable') if net else None,
        },
        'last': {
            'addr': Ansible_utils_ipaddr(Ansible_utils_ipaddr(net, '-1'), 'address') if net else None,
            'cidr': Ansible_utils_ipaddr(net, '-1') if net else None,
            'usable': Ansible_utils_ipaddr(net, 'last_usable') if net else None,
        },
        'range': {
            'usable': str(Ansible_utils_ipaddr(net, 'range_usable')).split('-', 2) if net and size_net and size_net > 1 else None,
        }
    }

def as_ip_segments_validated(data, on_invalid: t.Optional[t.Callable] = None, **kwargs)-> list:
    ret = Data_map(to_iterable(data), lambda ip_: as_ip_segments(ip_))

    if Validate_filled(ret) and Validate_filled(on_invalid):
        for idx, item in enumerate(ret):
            if Data_get(item, 'ctrl.valid') == True:
                continue
            
            if on_invalid:
                e = Utils_call(on_invalid, item, idx)
                if Validate_is_exception(e):
                    raise e
        
    return list(ret)

def as_ip_merged_cidrs(value, action="merge"):
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
    data: t.Union[t.Sequence[t.Any], t.Mapping[t.Any, t.Any]], 
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
    data: t.Union[t.Sequence[t.Any], t.Mapping[t.Any, t.Any]], 
    **kwargs,
)-> str:
    import yaml
    return yaml.dump(data, **kwargs)
### END: Yaml

### BEGIN: Lua
def from_lua(data: str, **kwargs)-> dict|list:
    import luadata
    return luadata.unserialize(data, **kwargs)

def to_lua(data: t.Mapping|t.Sequence, **kwargs)-> str:
    import luadata
    return luadata.serialize(data, **kwargs)
### END: Lua

### BEGIN: Toml
def from_toml(data: str)-> dict|list:
    from tomlkit import parse
    return parse(data)

def to_toml(data: t.Mapping, **kwargs)-> str:
    from tomlkit import dumps
    return dumps(data, **kwargs)
### END: Toml

### BEGIN: Toml
def from_base64(data: t.Any, **kwargs)-> str|bytes:
    import base64
    decode_as = kwargs.pop('decode', 'utf-8')

    ret = base64.b64decode(to_text(data), **kwargs)

    if Validate_filled(decode_as):
        return ret.decode(decode_as)
    
    return ret

def to_base64(data: t.Any, **kwargs)-> str|bytes:
    import base64
    decode_as = kwargs.pop('decode', 'utf-8')
    encode_as = kwargs.pop('encode', 'utf-8')
    
    data = str(to_text(data))
    if Validate_filled(encode_as):
        data = data.encode(encode_as)
    
    ret = base64.b64encode(data, **kwargs)

    if Validate_filled(decode_as):
        return ret.decode(decode_as)

    return ret
### END: Toml

### BEGIN: Uuid
def to_uuid(data: str | bytes) -> uuid.UUID:
    data = to_text(data)
    return uuid.UUID(hex=data)
### END: Uuid

### BEGIN: Roles
def from_file_known_hosts(file_content: str)-> list[dict[str,str]]:
    import re
    ret = []

    for line in iter(str(file_content).splitlines()):
        normalised = re.sub(r'\s+', ' ', str(line).strip())
        segments = list(normalised.split(maxsplit=2))
        hash_ = str(Data_get(segments, '0', ''))
        type_ = str(Data_get(segments, '1', ''))
        key_ = str(Data_get(segments, '2', ''))

        if Validate_blank(hash_) or Validate_blank(type_) or Validate_blank(key_) or not type_.startswith('ssh-'):
            ret.append({'raw': line})
            continue

        if hash_.startswith('|1|'):
            hash_segments = list(Str_chop_start(hash_, '|1|').split(sep='|', maxsplit=2))
            hmac_key = str(Data_get(hash_segments, '0', ''))
            hmac_hash = str(Data_get(hash_segments, '1', ''))
            if Validate_blank(hmac_key) or Validate_blank(hmac_hash):
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

### BEGIN: Callable
def to_callable_signature(callback: t.Callable) -> inspect.Signature:
    return inspect.signature(callback)

def to_callable_parameters(
    callback: t.Callable,
    kinds: ENUMERATABLE[CallableParameterKind] = []
) -> tt.MappingProxyType[str, t.Any]:
    ret = to_callable_signature(callback).parameters

    if kinds:
        ret = Data_where(
            ret, 
            lambda param: Validate_callable_parameter_is_kind(param, *kinds),
            {},
        )

    return tt.MappingProxyType(ret)

def as_callable_segments(callback: t.Callable) -> tt.MappingProxyType[str, t.Any]:
    sig = to_callable_signature(callback)
    is_named = callback.__name__ != '<lambda>'
    ret = {
        'name': callback.__name__ if is_named else None,
        'is': {
            'named': is_named,
            'anonymous': not is_named,
        },
        'has': {
            'params': {
                'pos': 0,
                'key': 0,
                'any': 0,
                'args': 0,
                'kwargs': 0,
                'empty': 0,
            },
        },
        'params': [],
    }
    
    for pos, name in enumerate(sig.parameters.keys()):
        param = sig.parameters[name]
        type_ = CallableParameterTypeMap[param.kind]
        
        has_default = Validate_callable_parameter_has(param, 'default')
        has_annotation = Validate_callable_parameter_has(param, 'annotation')
        ret['params'].append({
            'pos': pos,
            'type': type_,
            'name': name,
            'annotation': param.annotation,
            'default': param.default if has_default else None,
            'item': param,
            'kind': param.kind,
            'has': {
                'default': has_default,
                'annotation': has_annotation,
            },
        }) 

        ret['has']['params'][type_] += 1

    return tt.MappingProxyType(ret)

def as_callable_caller_segments(container: object, origin: str) -> tt.MappingProxyType[str, t.Any]:
    import sys
    ret = {
        'mros': as_non_native_types(type(container).__mro__),
        'items': [],
    }

    level = 0
    while True:
        level += 1
        try:
            frame = sys._getframe(level)
            item = {
                'level': level,
                'self': frame.f_locals.get('self'),
                'class': frame.f_locals.get('self').__class__,
                'caller_code': frame.f_code,
                'caller_name': frame.f_code.co_name,
                'indirects': [],
            }

            for cls in ret['mros']:
                indirect = cls.__dict__.get(item['caller_name'])
                if Validate_filled(indirect):
                    item['indirects'].append({'class': indirect.__class__, 'code': getattr(indirect, '__code__', None)})
                
            ret['items'].append(tt.MappingProxyType(item))
        except Exception:
            break
    
    return tt.MappingProxyType(ret)
### END: Callable