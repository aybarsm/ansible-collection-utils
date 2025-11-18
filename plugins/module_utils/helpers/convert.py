import typing as T
import datetime
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    __data, __factory, __utils, __validate, __ipaddress, __hashlib
)

def to_pydash(data: T.Union[T.Sequence[T.Any], T.Mapping[T.Any, T.Any]])-> dict|list:
    if __validate().is_sequence(data):
        return list(data)
    else:
        return dict(data)

def to_ip_address(data, **kwargs):
    ph = __factory().placeholder(mod='hashed')
    default = kwargs.get('default', ph)

    try:
        return __ipaddress().ip_address(data)
    except Exception as e:
        if default == ph:
            raise e
        
        return default
    
def to_ip_network(data, **kwargs):
    ph = __factory().placeholder(mod='hashed')
    default = kwargs.get('default', ph)

    try:
        return __ipaddress().ip_network(data)
    except Exception as e:
        if default == ph:
            raise e
        
        return default

def to_md5(data: T.Any) -> str:
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
    return list(data) if __validate().is_sequence(data) else [data]

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
        return lambda entry: all([__data().has(entry, key) and __data().get(entry, key) == val for key, val in data.items()])

def to_data_key(*args: str, **kwargs)-> str:
    import re
    include_blanks = __validate().truthy(kwargs.pop('blanks', False))
    ret = []
    
    for key in args:
        key = re.sub(r'\.+', '.', key).strip('.')
        if include_blanks or __validate().filled(key):
            ret.append(key)
    
    return '.'.join(ret)

def to_safe_json(data):
    if __validate().is_bytes(data):
        return to_safe_json(to_text(data))
    elif __validate().is_string(data) and __validate().str_is_json(data):
        return to_safe_json(__utils().json_parse(data))
    elif __validate().is_string(data) and __validate().str_is_yaml(data):
        return to_safe_json(__utils().yaml_parse(data))
    elif isinstance(data, (str, int, float, bool)) or data is None:
        return data
    elif __validate().is_ansible_mapping(data):
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

    if __validate().is_string(variable) and not is_trusted_as_template(variable):
        variable = trust_as_template(variable)
    
    for var_key, var_value in extra_vars.items():
        templar.available_variables[var_key] = var_value
    
    ret = templar.template(variable, **kwargs)
    
    if not __validate().falsy(remove_extra_vars):
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

### BEGIN: Ansible

### END: Ansible