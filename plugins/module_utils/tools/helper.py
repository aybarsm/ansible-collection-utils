from __future__ import annotations
import json, yaml, inspect, pathlib, os, io, datetime, random, uuid, string, tempfile, rich.pretty, rich.console
from collections.abc import Mapping, Sequence
from typing import Union
from ansible_collections.aybarsm.utils.plugins.module_utils.tools import Str, Data, Validate

class Helper:
    @staticmethod
    def to_type_name(data):
        return type(data).__name__

    @staticmethod
    def to_ip_address(data):
        from ansible_collections.ansible.utils.plugins.plugin_utils.base.ipaddress_utils import ip_address
        try:
            return ip_address(data)
        except Exception as e:
            return e
        
    @staticmethod
    def to_ip_network(data):
        from ansible_collections.ansible.utils.plugins.plugin_utils.base.ipaddress_utils import ip_network
        try:
            return ip_network(data)
        except Exception as e:
            return e
            
    @staticmethod
    def save_as_json(content: Mapping | Sequence | str, path: str, **kwargs) -> None:
        overwrite = kwargs.pop('overwrite', False)

        if Validate.file_exists(path) and not overwrite:
            return
        
        if Validate.is_mapping(content):
            content = json.dumps(Helper.to_safe_json(dict(content)), **kwargs)
        elif Validate.is_sequence(content):
            content = json.dumps(Helper.to_safe_json(list(content)), **kwargs)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(content))

    @staticmethod
    def path_rglob(path: pathlib.Path | str):
        path = pathlib.Path(path)
        return path.rglob("*")
    
    @staticmethod
    def callable_signature(callback):
        return inspect.signature(callback)
    
    @staticmethod
    def positional_argument_count(callback):
        return int(sum(
            1 for param in Helper.callable_signature(callback).parameters.values()
            if param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ))
    
    @staticmethod
    def required_positional_argument_count(callback):
        return int(sum(
            1 for param in Helper.callable_signature(callback).parameters.values()
            if param.default == inspect.Parameter.empty and
            param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ))
        
    @staticmethod
    def callable_args_name(callback):
        for name, param in Helper.callable_signature(callback).parameters.items():
            if param.kind == inspect.Parameter.VAR_POSITIONAL:
                return name
        
        return None

    @staticmethod
    def callable_kwargs_name(callback):
        for name, param in Helper.callable_signature(callback).parameters.items():
            if param.kind == inspect.Parameter.VAR_KEYWORD:
                return name
        
        return None
    
    @staticmethod
    def callable_kwargs_defaults(callback):        
        return {
            k: v.default
            for k, v in Helper.callable_signature(callback).parameters.items()
            if v.default is not inspect.Parameter.empty
        }
    
    @staticmethod
    def callback(callback, *args, **kwargs):
        if Helper.callable_args_name(callback) == None:
            take = int(min([len(list(args)), Helper.positional_argument_count(callback)]))
            args = list(list(args)[:take])

        return callback(*args, **kwargs) if Helper.callable_kwargs_name(callback) != None else callback(*args)
    
    @staticmethod
    def join_paths(*args, **kwargs):
        normalize = kwargs.pop('normalize', True)
        
        args = list(args)
        for idx in range(0, len(args)):
            args[idx] = str(args[idx]).strip().rstrip(os.sep).strip()

        ret = os.path.join(*args)
        if normalize:
            ret = os.path.normpath(ret)

        return str(ret)
    
    @staticmethod
    def realpath(path):
        return os.path.realpath(path)
    
    @staticmethod
    def resolve_path(path, **kwargs):
        if kwargs.get('realpath', False):
            path = Helper.realpath(path)
        return path
    
    @staticmethod
    def dump(*args, **kwargs):
        if Validate.is_env_ansible():
            from ansible.utils.display import Display
            buffer = io.StringIO()
            console = rich.console.Console(file=buffer, force_terminal=False)
            for arg in args:
                console.print(rich.pretty.Pretty(arg, **kwargs))

            display = Display()
            display.display(buffer.getvalue())
        else:
            for arg in args:
                rich.pretty.pprint(arg, **kwargs)
    
    @staticmethod
    def ts(**kwargs):
        ts = datetime.datetime.now(datetime.timezone.utc)
        mod = kwargs.get('mod', '')
        
        if mod in ['str', 'string']:
            return str(ts.strftime("%Y-%m-%dT%H:%M:%SZ"))
        elif mod == 'safe':
            return str(ts.strftime("%Y%m%dT%H%M%SZ"))
        elif mod == 'long':
            return str(ts.strftime("%Y-%m-%dT%H:%M:%S") + f".{ts.microsecond * 1000:09d}Z")
        elif mod == 'long_safe':
            return str(ts.strftime("%Y%m%dT%H%M%S") + f".{ts.microsecond * 1000:09d}Z")
        elif mod == 'timestamp':
            return int(ts.timestamp())
        else:
            return ts
    
    @staticmethod
    def placeholder(randLen = 32, **kwargs):
        now = Helper.ts()

        ret = str('|'.join([
            ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(math.ceil(randLen/2))),
            now.strftime("%Y-%m-%dT%H:%M:%S") + f".{now.microsecond * 1000:09d}Z", #type: ignore
            ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(math.floor(randLen/2)))
        ]))

        mod = kwargs.get('mod', '')
        
        if mod in ['hash', 'hashed']:
            return Str.to_md5(ret)
        else:
            return ret
    
    @staticmethod
    def uuid(**kwargs):
        ver = kwargs.get('ver', 4)
        if ver not in [1, 3, 4, 5]:
            raise ValueError(f'Invalid uuid version [{ver}]')
        
        namespace = kwargs.get('namespace', '')
        name = kwargs.get('name', '')
        if ver in [3, 5] and (Validate.blank(namespace) or Validate.blank(name)):
            raise ValueError(f'uuid version [{ver}] requires namespace and name')
        
        raw = kwargs.get('raw', False)
        
        if ver == 1:
            ret = uuid.uuid1()
        elif ver == 3:
            ret = uuid.uuid3(namespace, name)
        elif ver == 4:
            ret = uuid.uuid4()
        elif ver == 5:
            ret = uuid.uuid5(namespace, name)
        
        return ret if raw == True else str(ret)
    
    @staticmethod
    def ensure_directory_exists(path: Union[pathlib.Path, str]) -> None:
        path = pathlib.Path(path)
        path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def path_tmp(path:str, *args, **kwargs) -> str:
        is_dir = kwargs.pop('dir', False)
        args = list(args)
        ensure_directory_exists = is_dir or len(args) > 0
        args = [tempfile.gettempdir(), path] + args
        ret = Helper.join_paths(*args)
        
        if ensure_directory_exists:
            path_dir = ret if is_dir else Helper.dirname(ret)
            Helper.ensure_directory_exists(path_dir)
        
        return ret

    @staticmethod
    def to_ansible_type(data):
        match data:
            case 'str' | 'string':
                return 'str'
            case 'int' | 'integer':
                return 'integer'
            case 'bool' | 'boolean':
                return 'bool'
            case 'float' | 'double' | 'number':
                return 'float'
            case 'list' | 'array' | 'arr':
                return 'list'
            case 'dict' | 'object':
                return 'dict'
            case 'path' | 'file':
                return 'path'
            case _:
                raise ValueError(f"Undefined to_ansible_type: {data}")
    
    @staticmethod
    def to_iterable(data) -> list:
        return list(data) if Validate.is_sequence(data) else [data]
    
    @staticmethod
    def to_querystring(data, keyAttr, valAttr=None, assignChar='=', joinChar='&', recurse=None, recurseIndentSteps=0, recurseIndentChar=' ', repeatJoinCharOnMainLevels=False):
        if Validate.is_dict(data):
            data = [data]

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

    @staticmethod
    def mapping_to_str(data: Mapping, **kwargs) -> str:
        data = dict(data)
        char_assign = kwargs.pop('assign', '=')
        char_join = kwargs.pop('join', '&')
        as_str = kwargs.pop('as_str', True)
        result = []

        for key, value in data.items():
            if as_str:
                if Validate.is_bool(value):
                    value = 'true' if value else 'false'
                else:
                    value = str(value)
            
            result.append(f'{key}{char_assign}{value}')

        return char_join.join(result).strip(char_join)
    
    @staticmethod
    def hostvars_to_dict(obj):
        result = {}
        for host in obj:
            try:
                raw_vars = obj.raw_get(host)
                result[host] = Helper.to_safe_json(raw_vars)
            except Exception as e:
                result[host] = f"<error extracting hostvars for {host}: {e}>"
        return result
    
    @staticmethod
    def hostvarsvars_to_dict(obj):
        try:
            return Helper.to_safe_json(obj._vars)
        except Exception as e:
            return f"<error extracting HostVarsVars: {e}>"
    
    @staticmethod
    def lazytemplatedict_to_dict(obj):
        try:
            return Helper.to_safe_json(dict(obj.items()))
        except Exception as e:
            return f"<error extracting HostVarsVars: {e}>"
    
    @staticmethod
    def to_safe_json(data):
        
        if Validate.is_bytes(data):
            return Helper.to_safe_json(Helper.to_native(data))
        elif Validate.is_string(data) and Validate.str_is_json(data):
            return Helper.to_safe_json(json.loads(data))
        elif Validate.is_string(data) and Validate.str_is_yaml(data):
            return Helper.to_safe_json(yaml.safe_load(data))
        elif isinstance(data, (str, int, float, bool)) or data is None:
            return data
        elif Validate.is_hostvars(data):
            return Helper.hostvars_to_dict(data)
        elif Validate.is_hostvarsvars(data):
            return Helper.hostvarsvars_to_dict(data)
        elif Validate.is_lazytemplatedict(data):
            return Helper.lazytemplatedict_to_dict(data)
        elif isinstance(data, dict):
            return {str(k): Helper.to_safe_json(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return [Helper.to_safe_json(item) for item in data]
        elif hasattr(data, '__str__'):
            try:
                return str(data)
            except Exception:
                return "<unserializable object>"

        # Fallback
        return f"<unsupported type: {type(data)}>"
    
    @staticmethod
    def top_level_dirs(paths, *args, **kwargs):
        if Validate.blank(paths):
            return []

        ret = []

        norm_paths = sorted(set(os.path.normpath(p) for p in paths), key=lambda p: p.count(os.sep), reverse=True)
        for path in norm_paths:
            if not any(os.path.commonpath([path, existing]) == path for existing in ret):
                ret.append(path)

        return ret
    
    @staticmethod
    def to_list_dicts(data, defaults={}, *args, **kwargs):
        no_dot = kwargs.get('no_dot', False)
        ret = []

        for keyIndex in range(0, len(data[list(data.keys())[0]])):
            new_item = defaults.copy()

            for dataKey in data.keys():
                if no_dot:
                    new_item[dataKey] = data[dataKey][keyIndex]
                else:
                    Data.set(new_item, dataKey, data[dataKey][keyIndex])

            ret.append(new_item)

        return ret
    
    @staticmethod
    def dirname(path):
        return os.path.dirname(path)

    @staticmethod
    def basename(path):
        return os.path.basename(path)
    
    @staticmethod
    def to_native(*args, **kwargs):
        from ansible.module_utils.common.text.converters import to_native
        return to_native(*args, **kwargs)
    
    @staticmethod
    def to_string(data, **kwargs):
        return str(Helper.to_native(data, **kwargs))

    @staticmethod
    def fetch_url_to_module_result(resp, info, **kwargs):
        status_min = int(kwargs.pop('status_min', 200))
        status_max = int(kwargs.pop('status_max', 300))
        status = int(info.get('status', -1))

        ret = {
            'failed': True,
            'msg': '',
            'kwargs': {
                'status': status,
            }
        }
        
        if not status >= status_min and not status < status_max:
            msg = {'Message': info.get('msg')}

            if Validate.filled(info.get('exception', '')):
                msg['Exception'] = info.get('exception', '')
            
            ret['msg'] = Helper.mapping_to_str(msg, assign=': ', join=' | ')
            
            err_body = None
            if Validate.is_http_response(resp):
                err_body = Helper.to_native(resp.read())
            elif Validate.filled(info.get('body', '')):
                err_body = Helper.to_native(info.get('body', ''))
                
            if Validate.filled(err_body):
                ret['kwargs']['body'] = err_body
        else:
            ret['failed'] = False
            ret['content'] = Helper.to_native(resp.read()) # type: ignore
            
            if Validate.str_is_json(ret['content']):
                ret['content'] = json.loads(ret['content'])
        
        return ret
    
    @staticmethod
    def ip_as_addr(data) -> str:
        data = str(data)
        if '/' not in data:
            return data

        addr = Str.before(data, '/')

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
    
    @staticmethod
    def subnets_collapse(data, **kwargs) -> list:
        ret = []
        only = kwargs.pop('only', '')
        only_private = only in ['pri', 'private']
        only_public = only in ['pub', 'public']

        proto = kwargs.pop('proto', '')
        only_v4 = proto in ['4', 'v4', 4]
        only_v6 = proto in ['6', 'v6', 6]

        for subnet in data:
            addr = Helper.ip_as_addr(subnet)
            
            if (only_private and Validate.is_ip_public(addr)) or (only_public and Validate.is_ip_private(addr)):
                continue

            if (only_v4 and Validate.is_ip_v6(addr)) or (only_v6 and Validate.is_ip_v4(addr)):
                continue

            supernets = list(set(data) - set([subnet]))
            if not any([Validate.is_subnet_of(subnet, supernet) for supernet in supernets]):
                ret.append(subnet)

        return ret
    
    @staticmethod
    def mapping_to_lua(data: Mapping) -> str:
        data = Helper.to_safe_json(dict(data))
        ret = json.dumps(data, separators=(",",":"))

        if ret.startswith('['):
            ret = '{' + Str.after('[', ret)
        
        if ret.endswith(']'):
            ret = Str.before_last(']', ret) + '}'

        return ret