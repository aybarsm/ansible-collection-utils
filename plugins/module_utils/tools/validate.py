from __future__ import annotations
import sys, pathlib, os, json, yaml, re, urllib.parse
from collections.abc import Mapping, MutableMapping, Sequence, MutableSequence
from typing import Union
from ansible_collections.aybarsm.utils.plugins.module_utils.tools import Helper, Jinja, Str

_DEFAULTS = {
    "ansible": {
        "entrypoints":
            [
                "ansible.cli.adhoc",
                "ansible_builder.cli",
                "ansible_collections.ansible_community",
                "ansible.cli.config",
                "ansible.cli.console",
                "ansible.cli.doc",
                "ansible.cli.galaxy",
                "ansible.cli.inventory",
                "ansiblelint.__main__",
                "ansible.cli.playbook",
                "ansible.cli.pull",
                "ansible_test._util.target.cli.ansible_test_cli_stub",
                "ansible.cli.vault",
            ]
    },
}

class Validate:
    @staticmethod
    def is_truthy(data):
        return Helper.to_string(data).lower() in ('y', 'yes', 'on', '1', 'true', 't', 1, 1.0)
    
    @staticmethod
    def is_falsy(data):
        return Helper.to_string(data).lower() in ('n', 'no', 'off', '0', 'false', 'f', 0, 0.0)
    
    @staticmethod
    def is_type_name(data, name: str):
        return Helper.to_type_name(data) == name
    
    @staticmethod
    def is_exception(data):
        return isinstance(data, BaseException) or (isinstance(data, type) and issubclass(data, BaseException))
    
    @staticmethod
    def is_ip_v4(data):
        ip = Helper.to_ip_address(data)
        return ip.version == 4 if not Validate.is_exception(data) else False #type: ignore
    
    @staticmethod
    def is_ip_v6(data):
        ip = Helper.to_ip_address(data)
        return ip.version == 6 if not Validate.is_exception(data) else False #type: ignore
    
    @staticmethod
    def is_ip_public(data):
        ip = Helper.to_ip_address(data)
        return ip.is_global if not Validate.is_exception(data) else False #type: ignore
    
    @staticmethod
    def is_ip_private(data):
        ip = Helper.to_ip_address(data)
        return ip.is_private if not Validate.is_exception(data) else False #type: ignore
    
    @staticmethod
    def is_subnet_of(network_a, network_b):
        network_a = Helper.to_ip_network(network_a)
        network_b = Helper.to_ip_network(network_b)
        
        if Validate.is_exception(network_a) or Validate.is_exception(network_b):
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
    
    @staticmethod
    def is_supernet_of(network_a, network_b):
        return Validate.is_subnet_of(network_b, network_a)
    
    @staticmethod
    def is_http_error(data):
        import urllib.error
        return Validate.is_object(data) and isinstance(data, urllib.error.HTTPError)

    @staticmethod
    def is_http_response(data):
        import http.client
        return Validate.is_object(data) and isinstance(data, http.client.HTTPResponse)
    
    @staticmethod
    def is_int_even(data: int) -> bool:
        return data % 2 == 0
    
    @staticmethod
    def is_int_odd(data: int) -> bool:
        return not Validate.is_int_even(data)
    
    @staticmethod
    def is_env_ansible():
        return any(mod in sys.modules for mod in _DEFAULTS['ansible']['entrypoints'])

    @staticmethod
    def is_string(data):
        return isinstance(data, str)

    @staticmethod
    def is_list(data):
        return isinstance(data, list)
    
    @staticmethod
    def is_tuple(data):
        return isinstance(data, tuple)
    
    @staticmethod
    def is_iterable(data, **kwargs) -> bool:
        return Validate.is_sequence(data, **kwargs)
    
    @staticmethod
    def is_dict(data):
        return isinstance(data, dict)
    
    @staticmethod
    def is_bool(data):
        return isinstance(data, bool)
    
    @staticmethod
    def is_object(data):
        return isinstance(data, object)
    
    @staticmethod
    def is_omitted(data):
        return Validate.is_string(data) and str(data).startswith('__omit_place_holder__')
    
    @staticmethod
    def is_defined(data):
        return not Validate.is_undefined(data)
    
    @staticmethod
    def is_undefined(data):
        return Validate.is_object(data) and type(data).__name__.startswith('AnsibleUndefined')
    
    @staticmethod
    def is_hostvars(data):
        return Validate.is_object(data) and type(data).__name__ == 'HostVars'
    
    @staticmethod
    def is_hostvarsvars(data):
        return Validate.is_object(data) and type(data).__name__ == 'HostVarsVars'
    
    @staticmethod
    def is_lazytemplatedict(data):
        return Validate.is_object(data) and type(data).__name__ == '_AnsibleLazyTemplateDict'
    
    @staticmethod
    def is_ansible_mapping(data):
        return Validate.is_hostvars(data) or Validate.is_hostvarsvars(data) or Validate.is_lazytemplatedict(data)
    
    @staticmethod
    def is_int(data):
        return isinstance(data, int)

    @staticmethod
    def is_float(data):
        return isinstance(data, float)
    
    @staticmethod
    def is_none(data):
        return data is None
    
    @staticmethod
    def is_callable(data):
        return callable(data)
    
    @staticmethod
    def is_bytes(data):
        return isinstance(data, bytes)
    
    @staticmethod
    def is_bytearray(data):
        return isinstance(data, bytearray)
    
    @staticmethod
    def is_mapping(data):        
        return isinstance(data, Mapping)
    
    @staticmethod
    def is_object_path(data):
        return isinstance(data, pathlib.Path)

    @staticmethod
    def is_sequence(data, include_strings = False):
        if not include_strings and Validate.is_string(data):
            return False
        
        return isinstance(data, Sequence)
    
    @staticmethod
    def is_list_of_dicts(data):
        return Validate.is_list(data) and all(Validate.is_dict(item) for item in data)
    
    @staticmethod
    def is_list_of_lists(data):
        return Validate.is_list(data) and all(Validate.is_list(item) for item in data)
    
    @staticmethod
    def is_list_of_tuples(data):
        return Validate.is_list(data) and all(Validate.is_tuple(item) for item in data)
    
    @staticmethod
    def is_dict_of_lists(data):
        return Validate.is_dict(data) and all(Validate.is_list(item) for item in data.values())
    
    @staticmethod
    def is_dict_of_dicts(data):
        return Validate.is_dict(data) and all(Validate.is_dict(item) for item in data.values())
    
    @staticmethod
    def is_dict_of_iterables(data):
        return Validate.is_dict(data) and all(Validate.is_iterable(item) for item in data.values())

    @staticmethod
    def is_list_of_strings(data):
        return Validate.is_list(data) and all(Validate.is_string(item) for item in data)
    
    @staticmethod
    def is_tuple_of_strings(data):
        return Validate.is_tuple(data) and all(Validate.is_string(item) for item in data)
    
    @staticmethod
    def is_iterable_of_strings(data):
        return Validate.is_iterable(data) and all(Validate.is_string(item) for item in data)
    
    @staticmethod
    def is_iterable_of_iterables(data):
        return Validate.is_iterable(data) and all(Validate.is_iterable(item) for item in data)
    
    @staticmethod
    def is_iterable_of_dicts(data):
        return Validate.is_iterable(data) and all(Validate.is_dict(item) for item in data)
    
    @staticmethod
    def is_list_of_bools(data):
        return Validate.is_list(data) and all(Validate.is_bool(item) for item in data)

    @staticmethod
    def is_blank(data):
        if Validate.is_string(data) and data.strip() == '':
            return True
        elif Validate.is_sequence(data) and len(data) == 0:
            return True
        elif Validate.is_mapping(data) and len(data.keys()) == 0:
            return True
        elif data is None:
            return True
        elif Validate.is_undefined(data):
            return True
        elif Validate.is_omitted(data):
            return True
        
        return False
    @staticmethod
    def is_filled(data):
        return not Validate.is_blank(data)
    
    @staticmethod
    def blank(data):
        return Validate.is_blank(data)
    
    @staticmethod
    def filled(data):
        return Validate.is_filled(data)
    
    @staticmethod
    def contains(data, *args, **kwargs):
        is_all = kwargs.get('all', False)
        args = list(args)
        
        return all([item in data for item in args]) if is_all else any([item in data for item in args])
    
    @staticmethod
    def is_type_of(data, check):
        req = str(check).lower().replace('_', '').replace('-', '')

        match req:
            case 'list':
                return Validate.is_list(data)
            case 'tuple':
                return Validate.is_tuple(data)
            case 'dict':
                return Validate.is_dict(data)
            case 'string':
                return Validate.is_string(data)
            case 'int' | 'integer':
                return Validate.is_int(data)
            case 'float':
                return Validate.is_float(data)
            case 'bool' | 'boolean':
                return Validate.is_bool(data)
            case 'none':
                return Validate.is_none(data)
            case 'listoflists' | 'listoflist':
                return Validate.is_list_of_lists(data)
            case 'listofdicts' | 'listofdict':
                return Validate.is_list_of_dicts(data)
            case 'listofstrings' | 'listofstring':
                return Validate.is_list_of_strings(data)
            case 'iterable':
                return Validate.is_iterable(data)
            case 'iterableofstrings':
                return Validate.is_iterable_of_strings(data)
            case 'listoftuples' | 'listoftuple':
                return Validate.is_list_of_tuples(data)
            case 'listofbooleans' | 'listofboolean' | 'listofbools' | 'listofbool':
                return Validate.is_list_of_bools(data)
            case 'tupleofstrings' | 'tupleofstring':
                return Validate.is_tuple_of_strings(data)
            case 'dictoflists' | 'dictoflist':
                return Validate.is_dict_of_lists(data)
            case 'dictofdicts' | 'dictofdict':
                return Validate.is_dict_of_dicts(data)
            case 'iterableofdicts':
                return Validate.is_iterable_of_dicts(data)
            case 'dictofiterables':
                return Validate.is_dict_of_iterables(data)
            case 'callable':
                return Validate.is_callable(data)
            case _:
                raise ValueError(f"require, {req} is not a valid type to check.")
    
    @staticmethod
    def require(required, data, *args, **kwargs):
        if not (Validate.is_string(required) or Validate.is_iterable_of_strings(required)):
            raise ValueError(f"validate.require, required must be string or iterable of strings, {type(required).__name__} given.")
        
        attr = kwargs.get('attr', '')
        fn = kwargs.get('fn', '')
        all = kwargs.get('all', False) == True

        results = []
        for req in Helper.to_iterable(required):
            results.append(Validate.is_type_of(data, req))

            if results[-1] and not all:
                break
        
        res = all(results) if all else any(results)

        if not res and Validate.filled(attr):
            msg = [
                '' if Validate.blank(fn) else f"{fn} :",
                attr,
                'must be',
                ', '.join(required),
                type(data).__name__,
                'given.'
            ]
            raise ValueError(', '.join(msg))
        
        return False
    
    @staticmethod
    def ansible(op_name, *args, **kwargs):
        jinja = Jinja()
        return jinja.test(op_name, *args, *kwargs)

    @staticmethod
    def is_file(path):
        return os.path.isfile(path)
    
    @staticmethod
    def is_file_readable(path: Union[pathlib.Path, str]) -> bool:
        path = pathlib.Path(path)
        if not path.exists() or not path.is_file():
            return False

        return os.access(path, os.R_OK)
    
    @staticmethod
    def is_file_writable(path: Union[pathlib.Path, str]) -> bool:
        path = pathlib.Path(path)
        if not path.exists() or not path.is_file():
            return False
        
        return os.access(path, os.W_OK)
    
    @staticmethod
    def is_dir(path):
        return os.path.isdir(path)
    
    @staticmethod
    def is_dir_readable(path: Union[pathlib.Path, str]) -> bool:
        path = pathlib.Path(path)
        if not path.exists() or not path.is_dir():
            return False

        return os.access(path, os.R_OK)
    
    @staticmethod
    def is_dir_writable(path: Union[pathlib.Path, str]) -> bool:
        path = pathlib.Path(path)
        if not path.exists() or not path.is_dir():
            return False
        
        return os.access(path, os.W_OK)
    
    @staticmethod
    def path_exists(path):
        return os.path.exists(path)
    
    @staticmethod
    def file_exists(path, **kwargs):
        path = Helper.resolve_path(path, **kwargs)

        return Validate.path_exists(path) and Validate.is_file(path)
    
    @staticmethod
    def dir_exists(path, **kwargs):        
        path = Helper.resolve_path(path, **kwargs)

        return Validate.path_exists(path) and Validate.is_dir(path)
    
    @staticmethod
    def is_json_string(data, type='any'):
        if not Validate.is_string(data):
            return False

        try:
            parsedData = json.loads(data)
            if type == 'object':
                return Validate.is_dict(parsedData)
            elif type == 'array':
                return Validate.is_iterable(parsedData)
            return True
        except (Exception):
            return False
    
    @staticmethod
    def is_yaml_string(data, type='any'):
        if not Validate.is_string(data):
            return False

        try:
            parsedData = yaml.safe_load(data)
            if type == 'object':
                return Validate.is_dict(parsedData)
            elif type == 'array':
                return Validate.is_iterable(parsedData)
            return Validate.is_dict(parsedData) or Validate.is_iterable(parsedData)
        except (Exception):
            return False
    
    @staticmethod
    def callable_has_args(data):        
        Validate.require('callable', data, 'callable')
        
        return Helper.callable_args_name(data) != None

    @staticmethod
    def callable_has_kwargs(data):        
        Validate.require('callable', data, 'callable')
        return Helper.callable_kwargs_name(data) != None
    
    @staticmethod
    def str_is_match(haystack, patterns, *args, **kwargs):
        kwargs = dict(kwargs)
        kwargs['prepare'] = True

        return Validate.str_is_regex(haystack, patterns, *args, **kwargs)

    @staticmethod
    def str_is_regex(haystack, patterns, *args, **kwargs):
        import re
        is_cli = kwargs.get('cli', False)
        is_all = kwargs.get('all', False)
        is_escape = kwargs.get('escape', False)
        is_prepare = kwargs.get('prepare', False)
        
        if is_cli and Validate.is_string(patterns):
            patterns = Str.to_cli(patterns)
        
        if Validate.is_blank(patterns):
            return True

        for pattern in Helper.to_iterable(patterns):
            if is_escape:
                pattern = re.escape(pattern)
            
            if is_prepare:
                pattern = Str.wrap(pattern, '^', '$')
            
            res = re.match(rf"{pattern}", haystack)

            if not is_all and res:
                return True
            elif is_all and not res:
                return False
        
        return is_all
    
    @staticmethod
    def mutable_mappings(a, b):
        if not (isinstance(a, MutableMapping) and isinstance(b, MutableMapping)):
            myvars = []
            for x in [a, b]:
                try:
                    myvars.append(json.dumps(x))
                except Exception:
                    myvars.append(Helper.to_native(x))
            raise ValueError("failed to combine variables, expected dicts but got a '{0}' and a '{1}': \n{2}\n{3}".format(
                a.__class__.__name__, b.__class__.__name__, myvars[0], myvars[1])
            )
    
    @staticmethod
    def str_is_int(data: str) -> bool:
        return re.match(r"^[-]?[0-9]+$", data) != None
    
    @staticmethod
    def str_is_unsigned_int(data: str) -> bool:
        return re.match(r"^[0-9]+$", data) != None
    
    @staticmethod
    def str_is_numeric(data: str) -> bool:
        return re.match(r"^[+-]?(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|\.\d+)$", data) != None
    
    @staticmethod
    def str_is_url(data: str) -> bool:
        try:
            result = urllib.parse.urlparse(data)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False
    
    @staticmethod
    def str_is_json(data, type='any'):
        if not Validate.is_string(data):
            return False

        try:
            parsedData = json.loads(data)
            if type == 'object':
                return Validate.is_mapping(parsedData)
            elif type == 'array':
                return Validate.is_sequence(parsedData)
            return True
        except (Exception):
            return False
    
    @staticmethod
    def str_is_yaml(data, type='any'):
        if not Validate.is_string(data):
            return False

        try:
            parsedData = yaml.safe_load(data)
            if type == 'object':
                return Validate.is_mapping(parsedData)
            elif type == 'array':
                return Validate.is_sequence(parsedData)
            return Validate.is_mapping(parsedData) or Validate.is_sequence(parsedData)
        except (Exception):
            return False