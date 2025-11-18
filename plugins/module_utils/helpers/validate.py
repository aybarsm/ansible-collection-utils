import typing as T
from pathlib import Path as PathlibPath
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    __CONF, __convert, __data, __str, __utils,
)

Convert = __convert()
Data = __data()
Str = __str()
Utils = __utils()

### BEGIN: Data
def is_blank(data: T.Any)-> bool:
    if is_string(data) and data.strip() == '':
        return True
    elif is_sequence(data) and len(data) == 0:
        return True
    elif is_mapping(data) and len(data.keys()) == 0:
        return True
    elif data is None:
        return True
    elif is_ansible_undefined(data):
        return True
    elif is_ansible_omitted(data):
        return True
    
    return False

def is_filled(data: T.Any)-> bool:    
    return not is_blank(data)

def blank(data: T.Any, **kwargs)-> bool:
    type_ = str(kwargs.get('type', ''))
    return is_blank(data) and (not is_filled(type_) or is_type_name(data, type_))

def filled(data: T.Any, **kwargs)-> bool:
    type_ = str(kwargs.get('type', ''))
    return is_filled(data) and (not is_filled(type_) or is_type_name(data, type_))

def is_truthy(data: T.Any)-> bool:
    return Convert.to_string(data).lower() in ('y', 'yes', 'on', 'true', '1', '1.0', 1, 1.0)

def is_falsy(data: T.Any)-> bool:
    return Convert.to_string(data).lower() in ('n', 'no', 'off', 'false', '0', '0.0', 0, 0.0)

def truthy(data: T.Any)-> bool:
    return is_truthy(data)

def falsy(data: T.Any)-> bool:
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

def contains(data: T.Union[T.Sequence, T.Mapping[T.Any, T.Any]], *args, **kwargs)-> bool:
    is_all = kwargs.get('all', False)
    ret = [item in data for item in args]
    
    return all(ret) if is_all else any(ret)
### END: Data

### BEGIN: Type
def __is_sequence_pre_check(data, include_strings: bool = False, include_bytes = False)-> bool:
    if not include_strings and is_string(data):
        return False
    
    if not include_bytes and is_bytes(data):
        return False
    
    return True

def is_string(data: T.Any)-> bool:
    return isinstance(data, str)

def is_list(data: T.Any)-> bool:
    return isinstance(data, list)

def is_tuple(data: T.Any)-> bool:
    return isinstance(data, tuple)

def is_set(data: T.Any)-> bool:
    return isinstance(data, set)

def is_sequence(data, include_strings: bool = False, include_bytes = False)-> bool:
    if not __is_sequence_pre_check(data, include_strings, include_bytes):
        return False
    
    return isinstance(data, T.Sequence)

def is_iterable(data, include_strings: bool = False, include_bytes = False)-> bool:
    if not __is_sequence_pre_check(data, include_strings, include_bytes):
        return False
    
    return isinstance(data, T.Iterable)

def is_mapping(data: T.Any)-> bool:
    return isinstance(data, T.Mapping)

def is_dict(data: T.Any)-> bool:
    return isinstance(data, dict)

def is_bool(data: T.Any)-> bool:
    return isinstance(data, bool)

def is_object(data: T.Any)-> bool:
    return isinstance(data, object)

def is_int(data: T.Any)-> bool:
    return isinstance(data, int)

def is_float(data: T.Any)-> bool:
    return isinstance(data, float)

def is_none(data: T.Any)-> bool:
    return data is None

def is_callable(data: T.Any)-> bool:
    return callable(data)

def is_bytes(data: T.Any)-> bool:
    return isinstance(data, bytes)

def is_bytearray(data: T.Any)-> bool:
    return isinstance(data, bytearray)

def is_path(data: T.Any)-> bool:
    import pathlib
    return isinstance(data, pathlib.Path)

def is_exception(data: T.Any)-> bool:
    return isinstance(data, BaseException) or (isinstance(data, type) and issubclass(data, BaseException))

def is_http_error(data: T.Any)-> bool:
    import urllib.error
    return is_object(data) and isinstance(data, urllib.error.HTTPError)

def is_http_response(data: T.Any)-> bool:
    import http.client
    return is_object(data) and isinstance(data, http.client.HTTPResponse)

def is_type_name(data: T.Any, *of: str)-> bool:
    for type_ in Convert.to_iterable(of):
        if Convert.to_type_name(data) == type_:
            return True
    
    return False

def is_type_module(data: T.Any, of: str)-> bool:
    return Convert.to_type_module(data) == of

def is_type_of(data: T.Any, check: str)-> bool:
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

def is_type(data: T.Any, *args: str, **kwargs)-> bool:
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
    if not (isinstance(a, T.MutableMapping) and isinstance(b, T.MutableMapping)):
        myvars = []
        for x in [a, b]:
            try:
                myvars.append(Convert.to_json(x))
            except Exception:
                myvars.append(Convert.to_text(x))
        raise ValueError("failed to combine variables, expected dicts but got a '{0}' and a '{1}': \n{2}\n{3}".format(
            a.__class__.__name__, b.__class__.__name__, myvars[0], myvars[1])
        )
### END: Type


### BEGIN: String
def str_is_int(data: str)-> bool:
    import re
    return re.match(r"^[-]?[0-9]+$", data) != None

def str_is_json(
    data: str, 
    type_: T.Literal['any', 'mapping', 'sequence'] = 'any'
)-> bool:
    try:
        parsed = Convert.from_json(data)
        ret = is_type(parsed, type_)
    except (Exception):
        ret = False
    
    return ret

def str_is_yaml(
    data: str, 
    type_: T.Literal['any', 'mapping', 'sequence'] = 'any'
)-> bool:
    try:
        parsed = Convert.from_yaml(data)
        ret = is_type(parsed, type_)
    except (Exception):
        ret = False
    
    return ret

def str_is_lua(
    data: str, 
    type_: T.Literal['any', 'mapping', 'sequence'] = 'any'
)-> bool:
    try:
        parsed = Convert.from_lua(data)
        ret = is_type(parsed, type_)
    except (Exception):
        ret = False
    
    return ret

def str_is_toml(
    data: str, 
    type_: T.Literal['any', 'mapping', 'sequence'] = 'any'
)-> bool:
    try:
        parsed = Convert.from_toml(data)
        ret = is_type(parsed, type_)
    except (Exception):
        ret = False
    
    return ret

def str_contains(data: str, *args: str, **kwargs: T.Mapping[str, bool])-> bool:
    if blank(data):
        return False
    
    is_all = kwargs.pop('all', False)
    ret = []
    for needle in args:
        if needle in data:
            ret.append(True)
            if not is_all:
                break

    return all(ret)

def str_contains_non_alphanum(haystack: str)-> bool:
    import re
    return re.search(r'[^A-Za-z0-9]', haystack) != None

def str_is_regex_match(
    haystack: str|T.Sequence[str],
    patterns: str|T.Sequence[str],
    *args,
    **kwargs,
)-> bool:
    import re
    is_cli = kwargs.get('cli', False)
    is_all = kwargs.get('all', False)
    is_escape = kwargs.get('escape', False)
    is_prepare = kwargs.get('prepare', False)
    
    haystack = Convert.to_iterable(haystack)
    patterns = Convert.to_iterable(patterns)
    
    if blank(patterns):
        return True
    
    if is_cli:
        patterns = Data.flatten(Data.map(
            patterns,
            lambda entry: Convert.from_cli(entry, iterable=True, stripped=True)
        ))
    
    for entry in Convert.to_iterable(haystack):
        for pattern in Convert.to_iterable(patterns):
            if is_escape:
                pattern = re.escape(pattern)
            
            if is_prepare:
                pattern = Str.wrap(pattern, '^', '$')
            
            res = re.match(rf"{pattern}", entry)

            if not is_all and res:
                return True
            elif is_all and not res:
                return False
    
    return is_all
### END: String

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
def __to_ip_address(data: T.Any):
    return Convert.to_ip_address(Convert.to_string(data), default=False)

def __to_ip_network(data: T.Any):
    return Convert.to_ip_network(Convert.to_string(data), default=False)

def is_ip(data: T.Any)-> bool:
    return __to_ip_address(data) != False

def is_network(data: T.Any)-> bool:
    return __to_ip_network(data) != False

def is_ip_v4(data: T.Any)-> bool:
    return __to_ip_address(data).version == 4

def is_ip_v6(data: T.Any)-> bool:
    return __to_ip_address(data).version == 6

def is_ip_public(data: T.Any)-> bool:        
    return __to_ip_address(data).is_global

def is_ip_private(data: T.Any)-> bool:
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
def is_python_native(data: T.Any)-> bool:
    return is_type_module(data, 'builtins')
### END: Python

### BEGIN: Ansible
def is_ansible_omitted(data: T.Any)-> bool:
    return is_string(data) and str(data).startswith('__omit_place_holder__')

def is_ansible_undefined(data: T.Any)-> bool:
    return is_object(data) and Convert.to_type_name(data).startswith('AnsibleUndefined')

def is_ansible_defined(data: T.Any)-> bool:
    return not is_ansible_undefined(data)

def is_ansible_hostvars(data: T.Any)-> bool:
    return is_object(data) and is_type_module(data, 'ansible.vars.hostvars') and is_type_name(data, 'HostVars')

def is_ansible_hostvarsvars(data: T.Any)-> bool:
    return is_object(data) and is_type_module(data, 'ansible.vars.hostvars') and is_type_name(data, 'HostVarsVars')

def is_ansible_lazytemplatedict(data: T.Any)-> bool:
    return is_object(data) and is_type_module(data, 'ansible._internal._templating._lazy_containers') and is_type_name(data, '_AnsibleLazyTemplateDict')

def is_ansible_mapping(data: T.Any)-> bool:
    return is_ansible_hostvars(data) or is_ansible_hostvarsvars(data) or is_ansible_lazytemplatedict(data)

def is_ansible_marker(data: T.Any)-> bool:
    return is_object(data) and is_type_module(data, 'ansible._internal._templating._jinja_common') and is_type_name(data, 'Marker')

def is_ansible_undefined_marker(data: T.Any)-> bool:
    return is_object(data) and is_type_module(data, 'ansible._internal._templating._jinja_common') and is_type_name(data, 'UndefinedMarker')

def is_ansible_tagged_object(data: T.Any)-> bool:
    return is_object(data) and is_type_module(data, 'ansible.module_utils._internal._datatag') and any("AnsibleTaggedObject" == cls.__name__ for cls in type(data).__mro__)

def is_ansible_tagged_data(data: T.Any)-> bool:
    return is_object(data) and is_type_module(data, 'ansible.module_utils._internal._datatag')

def is_ansible_tagged_date(data: T.Any)-> bool:
    return is_ansible_tagged_data(data) and is_type_name(data, '_AnsibleTaggedDate')

def is_ansible_tagged_time(data: T.Any)-> bool:
    return is_ansible_tagged_data(data) and is_type_name(data, '_AnsibleTaggedTime')

def is_ansible_tagged_datetime(data: T.Any)-> bool:
    return is_ansible_tagged_data(data) and is_type_name(data, '_AnsibleTaggedDateTime')

def is_ansible_tagged_str(data: T.Any)-> bool:
    return is_ansible_tagged_data(data) and is_type_name(data, '_AnsibleTaggedStr')

def is_ansible_tagged_int(data: T.Any)-> bool:
    return is_ansible_tagged_data(data) and is_type_name(data, '_AnsibleTaggedInt')

def is_ansible_tagged_float(data: T.Any)-> bool:
    return is_ansible_tagged_data(data) and is_type_name(data, '_AnsibleTaggedFloat')

def is_ansible_tagged_list(data: T.Any)-> bool:
    return is_ansible_tagged_data(data) and is_type_name(data, '_AnsibleTaggedList')

def is_ansible_tagged_set(data: T.Any)-> bool:
    return is_ansible_tagged_data(data) and is_type_name(data, '_AnsibleTaggedSet')

def is_ansible_tagged_tuple(data: T.Any)-> bool:
    return is_ansible_tagged_data(data) and is_type_name(data, '_AnsibleTaggedTuple')

def is_ansible_tagged_dict(data: T.Any)-> bool:
    return is_ansible_tagged_data(data) and is_type_name(data, '_AnsibleTaggedDict')

def is_ansible_env()-> bool:
    import sys
    return any(mod in sys.modules for mod in __CONF['validate']['ansible']['entrypoints'])
### END: Ansible