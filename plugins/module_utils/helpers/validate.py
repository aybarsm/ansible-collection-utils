import typing as t
import inspect
from pathlib import Path as PathlibPath
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    _CONF, __convert, __data, __str, __utils
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.types import (
    ENUMERATABLE, CallableParameterKindMap, CallableParameterKind, CallableParameterHas
)

Convert = __convert()
Data = __data()
Str = __str()
Utils = __utils()

### BEGIN: Data
def is_blank(data: t.Any)-> bool:
    if is_none(data):
        return True
    elif is_string(data) and data.strip() == '':
        return True
    elif is_sequence(data) and len(data) == 0:
        return True
    elif is_mapping(data) and len(data.keys()) == 0: #type: ignore
        return True
    elif is_ansible_undefined(data):
        return True
    elif is_ansible_omitted(data):
        return True
    
    return False

def is_filled(data: t.Any)-> bool:    
    return not is_blank(data)

def blank(data: t.Any, **kwargs)-> bool:
    type_ = str(kwargs.get('type', ''))
    return is_blank(data) and (not is_filled(type_) or is_type_name(data, type_))

def filled(data: t.Any, **kwargs)-> bool:
    type_ = str(kwargs.get('type', ''))
    return is_filled(data) and (not is_filled(type_) or is_type_name(data, type_))

def is_truthy(data: t.Any)-> bool:
    return Convert.to_string(data).lower() in ('y', 'yes', 'on', 'true', '1', '1.0', 1, 1.0)

def is_falsy(data: t.Any)-> bool:
    return Convert.to_string(data).lower() in ('n', 'no', 'off', 'false', '0', '0.0', 0, 0.0)

def truthy(data: t.Any)-> bool:
    return is_truthy(data)

def falsy(data: t.Any)-> bool:
    return is_falsy(data)

def is_copyable(data):
    import copy
    try:
        copy.copy(data)
        return True
    except Exception:
        return False

def is_deepcopyable(data):
    import copy
    try:
        copy.deepcopy(data)
        return True
    except Exception:
        return False

def contains(data: t.Iterable[t.Any], *args: str|int, **kwargs)-> bool:
    is_all = kwargs.pop('all', False) == True
    no_dot = kwargs.pop('no_dot', True) == False

    for key_ in args:
        res = Data.has(data, key_) if not no_dot else key_ in data
        
        if res and not is_all:
            return True
        elif not res and is_all:
            return False

    return True if is_all else False

def is_item_exec(data: t.Mapping)-> bool:
    return not truthy(Data.get(data, '_skip', False)) and not falsy(Data.get(data, '_keep', True))
### END: Data

### BEGIN: Type
def __is_sequence_pre_check(data, include_strings: bool = False, include_bytes = False)-> bool:
    if not include_strings and is_string(data):
        return False
    
    if not include_bytes and is_bytes(data):
        return False
    
    return True

def is_string(data: t.Any)-> bool:
    return isinstance(data, str)

def is_list(data: t.Any)-> bool:
    return isinstance(data, list)

def is_tuple(data: t.Any)-> bool:
    return isinstance(data, tuple)

def is_set(data: t.Any)-> bool:
    return isinstance(data, set)

def is_sequence(data, include_strings: bool = False, include_bytes = False)-> bool:
    if not __is_sequence_pre_check(data, include_strings, include_bytes):
        return False
    
    return isinstance(data, t.Sequence)

def is_iterable(data, include_strings: bool = False, include_bytes = False)-> bool:
    if not __is_sequence_pre_check(data, include_strings, include_bytes):
        return False
    
    return isinstance(data, t.Iterable)

def is_enumeratable(data: t.Any) -> bool:
    return isinstance(data, (list, tuple, list))

def is_enumeratable_of_mappings(data: t.Any) -> bool:
    return is_enumeratable(data) and all(is_mapping(item) for item in data)

def is_mapping(data: t.Any) -> bool:
    return isinstance(data, t.Mapping)

def is_mapping_of_mappings(data: t.Any)-> bool:
    return is_mapping(data) and all(is_mapping(item) for item in data.values())

def is_iterable_of_mappings(data: t.Any)-> bool:
    return is_iterable(data) and all(is_mapping(item) for item in data)

def is_iterable_of_not_mappings(data: t.Any)-> bool:
    return is_iterable(data) and all(not is_mapping(item) for item in data)

def is_dict(data: t.Any)-> bool:
    return isinstance(data, dict)

def is_bool(data: t.Any)-> bool:
    return isinstance(data, bool)

def is_object(data: t.Any)-> bool:
    return isinstance(data, object)

def is_int(data: t.Any)-> bool:
    return isinstance(data, int)

def is_float(data: t.Any)-> bool:
    return isinstance(data, float)

def is_none(data: t.Any)-> bool:
    return data is None

def is_callable(data: t.Any)-> bool:
    return callable(data)

def is_bytes(data: t.Any)-> bool:
    return isinstance(data, bytes)

def is_bytearray(data: t.Any)-> bool:
    return isinstance(data, bytearray)

def is_path(data: t.Any)-> bool:
    import pathlib
    return isinstance(data, pathlib.Path)

def is_exception(data: t.Any)-> bool:
    return isinstance(data, BaseException) or (isinstance(data, type) and issubclass(data, BaseException))

def is_http_error(data: t.Any)-> bool:
    import urllib.error
    return is_object(data) and isinstance(data, urllib.error.HTTPError)

def is_http_response(data: t.Any)-> bool:
    import http.client
    return is_object(data) and isinstance(data, http.client.HTTPResponse)

def is_type_name(data: t.Any, *of: str)-> bool:
    for type_ in Convert.to_iterable(of):
        if Convert.to_type_name(data) == type_:
            return True
    
    return False

def is_type_module(data: t.Any, of: str)-> bool:
    return Convert.to_type_module(data) == of

def is_type_of(data: t.Any, check: str)-> bool:
    import re
    req = re.sub(r'\_+', '_', re.sub(r'\-+', '-', check.lower())).strip('_')

    match req:
        case 'any':
            return True
        case 'list':
            return is_list(data)
        case 'tuple':
            return is_tuple(data)
        case 'dict':
            return is_dict(data)
        case 'str' | 'string':
            return is_string(data)
        case 'int' | 'integer':
            return is_int(data)
        case 'float':
            return is_float(data)
        case 'bool' | 'boolean':
            return is_bool(data)
        case 'none':
            return is_none(data)
        case 'sequence':
            return is_sequence(data)
        case 'iterable':
            return is_mapping(data)
        case 'mapping':
            return is_mapping(data)
        case 'callable':
            return is_callable(data)
        # case 'listoflists':
        #     return is_list_of_lists(data)
        # case 'listofdicts':
        #     return is_list_of_dicts(data)
        # case 'listofstrings':
        #     return is_list_of_strings(data)
        # case 'iterableofstrings':
        #     return is_iterable_of_strings(data)
        # case 'listoftuples':
        #     return is_list_of_tuples(data)
        # case 'listofbooleans' | 'listofboolean' | 'listofbools' | 'listofbool':
        #     return is_list_of_bools(data)
        # case 'tupleofstrings' | 'tupleofstring':
        #     return is_tuple_of_strings(data)
        # case 'dictoflists' | 'dictoflist':
        #     return is_dict_of_lists(data)
        # case 'dictofdicts' | 'dictofdict':
        #     return is_dict_of_dicts(data)
        # case 'iterableofdicts':
        #     return is_iterable_of_dicts(data)
        # case 'dictofiterables':
        #     return is_dict_of_iterables(data)
        case _:
            raise ValueError(f"require, {check} [{req}] is not a valid type to check.")

def is_type(data: t.Any, *args: str, **kwargs)-> bool:
        if 'any' in args:
            return True
        
        check_attr = kwargs.pop('attr', '')
        check_fn = kwargs.pop('fn', '')
        check_all = kwargs.pop('all', False)

        results = []
        for check in args:
            results.append(is_type_of(data, check))

            if results[-1] and not check_all:
                break
        
        result = all(results) if all else any(results)

        if not result and filled(check_attr):
            msg = [
                '' if blank(check_fn) else f"{check_fn} :",
                check_attr,
                'must be',
                ', '.join(args),
                type(data).__name__,
                'given.'
            ]
            raise ValueError(', '.join(msg))
        
        return False

def require_mutable_mappings(a, b):
    if not (isinstance(a, t.MutableMapping) and isinstance(b, t.MutableMapping)):
        myvars = []
        for x in [a, b]:
            try:
                myvars.append(Convert.to_json(x))
            except Exception:
                myvars.append(Convert.to_text(x))
        raise ValueError("failed to combine variables, expected dicts but got a '{0}' and a '{1}': \n{2}\n{3}".format(
            a.__class__.__name__, b.__class__.__name__, myvars[0], myvars[1])
        )

def is_callable_parameter(data: t.Any)-> bool:
    return isinstance(data, inspect.Parameter)
### END: Type


### BEGIN: String
def str_wrapped(data: str, wrapper: str)-> bool:
    return data.startswith(wrapper) and data.endswith(wrapper)

def str_starts(data: str, *args: str)-> bool:
    if blank(args):
        return False
    
    for needle in args:
        if data.startswith(needle):
            return True
    
    return False

def str_ends(data: str, *args: str)-> bool:
    if blank(args):
        return False
    
    for needle in args:
        if data.endswith(needle):
            return True
    
    return False

def str_is_int(data: str)-> bool:
    import re
    return re.match(r"^[-]?[0-9]+$", data) != None

def str_is_json(
    data: str, 
    type_: t.Literal['any', 'mapping', 'sequence'] = 'any'
)-> bool:
    try:
        parsed = Convert.from_json(data)
        ret = is_type(parsed, type_)
    except (Exception):
        ret = False
    
    return ret

def str_is_yaml(
    data: str, 
    type_: t.Literal['any', 'mapping', 'sequence'] = 'any'
)-> bool:
    try:
        parsed = Convert.from_yaml(data)
        ret = is_type(parsed, type_)
    except (Exception):
        ret = False
    
    return ret

def str_is_lua(
    data: str, 
    type_: t.Literal['any', 'mapping', 'sequence'] = 'any'
)-> bool:
    try:
        parsed = Convert.from_lua(data)
        ret = is_type(parsed, type_)
    except (Exception):
        ret = False
    
    return ret

def str_is_toml(
    data: str, 
    type_: t.Literal['any', 'mapping', 'sequence'] = 'any'
)-> bool:
    try:
        parsed = Convert.from_toml(data)
        ret = is_type(parsed, type_)
    except (Exception):
        ret = False
    
    return ret

def str_contains(data: str, *args: str, **kwargs: t.Mapping[str, bool])-> bool:
    if blank(data):
        return False
    
    is_all = kwargs.pop('all', False)
    for needle in args:
        res = str(needle) in data
        if res and not is_all:
            return True
        elif not res and is_all:
            return False

    return True if is_all else False

def str_contains_non_alphanum(data: str)-> bool:
    import re
    return re.search(r'[^A-Za-z0-9]', data) != None

def str_matches(data: str|t.Sequence[str], patterns, **kwargs)-> bool:
    return filled(Str.matches(data, patterns, **kwargs))
### END: String

### BEGIN: Callable
def callable_is_coroutine(data: t.Callable) -> bool:
    return inspect.iscoroutinefunction(data)

def callable_parameter_is_kind(data: inspect.Parameter, *args: CallableParameterKind) -> bool:
    for type_ in args:
        if data.kind == CallableParameterKindMap[type_]:
            return True

    return False

def callable_parameter_has(data: inspect.Parameter, of: CallableParameterHas) -> bool:
    return not callable_parameter_is_kind(data, 'empty') and hasattr(data, of) and getattr(data, of) != CallableParameterKindMap['empty']
### END: Callable

### BEGIN: Integer
def is_int_even(data: int)-> bool:
    return data % 2 == 0

def is_int_odd(data: int)-> bool:
    return not is_int_even(data)
### END: Integer

### BEGIN: Object
def object_has_method(obj, method: str)-> bool:
    return filled(obj) and filled(method) and hasattr(obj, method) and callable(getattr(obj, method))
### END: Object

### BEGIN: IP
def __to_ip_address(data: t.Any):
    return Convert.to_ip_address(Convert.to_string(data), default=False)

def __to_ip_network(data: t.Any):
    return Convert.to_ip_network(Convert.to_string(data), default=False)

def is_ip(data: t.Any)-> bool:
    return __to_ip_address(data) != False

def is_network(data: t.Any)-> bool:
    return __to_ip_network(data) != False

def is_ip_v4(data: t.Any)-> bool:
    return __to_ip_address(data).version == 4

def is_ip_v6(data: t.Any)-> bool:
    return __to_ip_address(data).version == 6

def is_ip_public(data: t.Any)-> bool:        
    return __to_ip_address(data).is_global

def is_ip_private(data: t.Any)-> bool:
    return __to_ip_address(data).is_private

def is_subnet_of(network_a, network_b)-> bool:
    network_a = __to_ip_network(network_a)
    network_b = __to_ip_network(network_a)
    
    if network_a == False or network_b == False:
        return False
    
    try:
        if network_a._version != network_b._version: #type: ignore
            return False
        return (
            network_b.network_address <= network_a.network_address #type: ignore
            and network_b.broadcast_address >= network_a.broadcast_address #type: ignore
        )
    except Exception:
        return False

def is_supernet_of(network_a, network_b)-> bool:
    return is_subnet_of(network_b, network_a)
### END: IP

### BEGIN: Crypto
def hmac_matches(hash_a, hash_b)-> bool:
    import hmac
    return hmac.compare_digest(hash_a, hash_b)

def is_host_matches_host_hash(hmac_key: str, hmac_hash: str, *args: str)-> bool:
    import hmac, hashlib, base64
    for host in args:
        computed_hash = hmac.new(base64.b64decode(hmac_key), to_bytes(host), hashlib.sha1).digest() #type: ignore
        if hmac.compare_digest(computed_hash, base64.b64decode(hmac_hash)):
            return True
    
    return False
### END: Crypto

### BEGIN: FS
def fs_path_exists(path: PathlibPath|str, **kwargs)-> bool:
    return PathlibPath(path).exists(**kwargs)

def fs_file_exists(path: PathlibPath|str, **kwargs)-> bool:
    path = PathlibPath(path)
    return path.exists(**kwargs) and path.is_file(**kwargs)

def fs_dir_exists(path: PathlibPath|str, **kwargs)-> bool:
    path = PathlibPath(path)
    return path.exists(**kwargs) and path.is_dir(**kwargs)
### END: FS

### BEGIN: Python
def is_python_native(data: t.Any)-> bool:
    return is_type_module(data, 'builtins')
### END: Python

### BEGIN: Ansible
def is_ansible_omitted(data: t.Any)-> bool:
    return is_string(data) and str(data).startswith('__omit_place_holder__')

def is_ansible_undefined(data: t.Any)-> bool:
    return is_object(data) and Convert.to_type_name(data).startswith('AnsibleUndefined')

def is_ansible_defined(data: t.Any)-> bool:
    return not is_ansible_undefined(data)

def is_ansible_hostvars(data: t.Any)-> bool:
    return is_object(data) and is_type_module(data, 'ansible.vars.hostvars') and is_type_name(data, 'HostVars')

def is_ansible_hostvarsvars(data: t.Any)-> bool:
    return is_object(data) and is_type_module(data, 'ansible.vars.hostvars') and is_type_name(data, 'HostVarsVars')

def is_ansible_lazy_container_module(data: t.Any)-> bool:
    return is_object(data) and is_type_module(data, 'ansible._internal._templating._lazy_containers')

def is_ansible_lazy_template_dict(data: t.Any)-> bool:
    return is_ansible_lazy_container_module(data) and is_type_name(data, '_AnsibleLazyTemplateDict')

def is_ansible_lazy_template_list(data: t.Any)-> bool:
    return is_ansible_lazy_container_module(data) and is_type_name(data, '_AnsibleLazyTemplateList')

def is_ansible_lazy_access_tuple(data: t.Any)-> bool:
    return is_ansible_lazy_container_module(data) and is_type_name(data, '_AnsibleLazyAccessTuple')

def is_ansible_lazy_template(data: t.Any)-> bool:
    return is_ansible_lazy_template_dict(data) or is_ansible_lazy_template_list(data) or is_ansible_lazy_access_tuple(data)

def is_ansible_mapping(data: t.Any)-> bool:
    return is_ansible_hostvars(data) or is_ansible_hostvarsvars(data) or is_ansible_lazy_template_dict(data)

def is_ansible_marker(data: t.Any)-> bool:
    return is_object(data) and is_type_module(data, 'ansible._internal._templating._jinja_common') and is_type_name(data, 'Marker')

def is_ansible_undefined_marker(data: t.Any)-> bool:
    return is_object(data) and is_type_module(data, 'ansible._internal._templating._jinja_common') and is_type_name(data, 'UndefinedMarker')

def is_ansible_tagged_object(data: t.Any)-> bool:
    return is_object(data) and is_type_module(data, 'ansible.module_utils._internal._datatag') and any("AnsibleTaggedObject" == cls.__name__ for cls in type(data).__mro__)

def is_ansible_tagged_data(data: t.Any)-> bool:
    return is_object(data) and is_type_module(data, 'ansible.module_utils._internal._datatag')

def is_ansible_tagged_date(data: t.Any)-> bool:
    return is_ansible_tagged_data(data) and is_type_name(data, '_AnsibleTaggedDate')

def is_ansible_tagged_time(data: t.Any)-> bool:
    return is_ansible_tagged_data(data) and is_type_name(data, '_AnsibleTaggedTime')

def is_ansible_tagged_datetime(data: t.Any)-> bool:
    return is_ansible_tagged_data(data) and is_type_name(data, '_AnsibleTaggedDateTime')

def is_ansible_tagged_str(data: t.Any)-> bool:
    return is_ansible_tagged_data(data) and is_type_name(data, '_AnsibleTaggedStr')

def is_ansible_tagged_int(data: t.Any)-> bool:
    return is_ansible_tagged_data(data) and is_type_name(data, '_AnsibleTaggedInt')

def is_ansible_tagged_float(data: t.Any)-> bool:
    return is_ansible_tagged_data(data) and is_type_name(data, '_AnsibleTaggedFloat')

def is_ansible_tagged_list(data: t.Any)-> bool:
    return is_ansible_tagged_data(data) and is_type_name(data, '_AnsibleTaggedList')

def is_ansible_tagged_set(data: t.Any)-> bool:
    return is_ansible_tagged_data(data) and is_type_name(data, '_AnsibleTaggedSet')

def is_ansible_tagged_tuple(data: t.Any)-> bool:
    return is_ansible_tagged_data(data) and is_type_name(data, '_AnsibleTaggedTuple')

def is_ansible_tagged_dict(data: t.Any)-> bool:
    return is_ansible_tagged_data(data) and is_type_name(data, '_AnsibleTaggedDict')

def is_ansible_env()-> bool:
    import sys
    return any(mod in sys.modules for mod in _CONF['validate']['ansible']['entrypoints'])
### END: Ansible