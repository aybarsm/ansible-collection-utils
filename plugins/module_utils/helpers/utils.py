import typing as T
from pathlib import Path as PathlibPath

from pydash import method
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    __convert, __data, __validate, __inspect
)

Convert = __convert()
Data = __data()
Validate = __validate()

def dump(*args, **kwargs):
    import rich, rich.pretty
    if Validate.is_ansible_env():
        import io
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

def dd(*args, **kwargs):
    dump(*args, **kwargs)
    exit(0)

### BEGIN: Json
def json_load(path: PathlibPath|str, **kwargs)-> dict|list:
    return Convert.from_json(fs_read(path), **kwargs)

def json_save(data, path: PathlibPath|str, **kwargs) -> None:
        path = PathlibPath(path)
        overwrite = kwargs.pop('overwrite', False)

        if path.exists() and not overwrite:
            raise ValueError(f'Json file [{str(path)}] already exists.')
        
        kwargs_path = Data.only_with(kwargs, 'encoding', 'errors')
        kwargs_json = Data.all_except(kwargs, 'encoding', 'errors', 'newline')
        
        data = Convert.from_yaml(Convert.to_text(data))

        if Validate.is_mapping(data):
            data = Convert.to_json(dict(data), **kwargs_json) #type: ignore
        elif Validate.is_sequence(data):
            data = Convert.to_json(list(data), **kwargs_json) #type: ignore
        
        fs_write(path, str(data), **kwargs_path) #type: ignore
### END: Json

### BEGIN: Callable
def callable_signature(callback: T.Callable):
    return __inspect().signature(callback)

def callable_args_name(callback: T.Callable)-> T.Optional[str]:
    for name, param in callable_signature(callback).parameters.items():
        if param.kind == __inspect().Parameter.VAR_POSITIONAL:
            return name
    
    return None

def callable_kwargs_name(callback: T.Callable)-> T.Optional[str]:
    for name, param in callable_signature(callback).parameters.items():
        if param.kind == __inspect().Parameter.VAR_KEYWORD:
            return name
    
    return None

def callable_kwargs_defaults(callback: T.Callable)-> T.Optional[dict]:
    return {
        k: v.default
        for k, v in callable_signature(callback).parameters.items()
        if v.default is not __inspect().Parameter.empty
    }

def callable_positional_argument_count(callback):
    return int(sum(
        1 for param in callable_signature(callback).parameters.values()
        if param.kind in (__inspect().Parameter.POSITIONAL_ONLY, __inspect().Parameter.POSITIONAL_OR_KEYWORD)
    ))

def call(callback: T.Callable, *args, **kwargs)-> T.Any:
    if callable_args_name(callback) == None:
        take = int(min([len(list(args)), callable_positional_argument_count(callback)]))
        args = list(list(args)[:take])

    return callback(*args, **kwargs) if callable_kwargs_name(callback) != None else callback(*args)
### END: Callable

### BEGIN: FS
def fs_dirname(path: PathlibPath|str)-> str:
    return str(PathlibPath(path).parent)

def fs_join_paths(*args, **kwargs):
    import os
    normalize = kwargs.pop('normalize', True)
    
    args = list(args)
    for idx in range(0, len(args)):
        args[idx] = str(args[idx]).strip().rstrip(os.sep).strip()

    ret = os.path.join(*args)
    if normalize:
        ret = os.path.normpath(ret)

    return str(ret)

def fs_ensure_directory_exists(path: PathlibPath|str)-> None:
    PathlibPath(path).mkdir(parents=True, exist_ok=True)

def fs_read(path: PathlibPath|str, **kwargs)-> str:
    return PathlibPath(path).read_text(**kwargs)

def fs_read_bytes(path: PathlibPath|str, **kwargs)-> bytes:
    return PathlibPath(path).read_bytes(**kwargs)

def fs_write(path: PathlibPath|str, data: str|bytes, **kwargs)-> None:
    path = PathlibPath(path)
    if Validate.is_string(data):
        path.write_text(str(data), **kwargs)
    else:
        path.write_bytes(data, **kwargs) #type: ignore

def fs_top_level_dirs(paths: str|T.Sequence[str], *args: str)-> list[str]:
    import os

    paths = list(paths)
    if Validate.filled(args):
        paths.extend(args)
    
    paths = list(set(paths))

    if Validate.blank(paths):
        return []

    ret = []

    norm_paths = sorted(set(os.path.normpath(p) for p in paths), key=lambda p: p.count(os.sep), reverse=True)
    for path in norm_paths:
        if not any(os.path.commonpath([path, existing]) == path for existing in ret):
            ret.append(path)

    return ret
### END: FS

### BEGIN: Net
def net_subnets_collapse(data: T.Sequence[str], **kwargs) -> list:
    only = kwargs.pop('only', '')
    proto = kwargs.pop('proto', '')

    only_private = only in ['pri', 'private']
    only_public = only in ['pub', 'public']
    only_v4 = proto in ['4', 'v4', 4]
    only_v6 = proto in ['6', 'v6', 6]
    
    ret = []

    for subnet in data:
        addr = Convert.as_ip_address(subnet)
        
        if (only_private and Validate.is_ip_public(addr)) or (only_public and Validate.is_ip_private(addr)):
            continue

        if (only_v4 and Validate.is_ip_v6(addr)) or (only_v6 and Validate.is_ip_v4(addr)):
            continue

        supernets = list(set(data) - set([subnet]))
        if not any([Validate.is_subnet_of(subnet, supernet) for supernet in supernets]):
            ret.append(subnet)

    return list(set(ret))
### BEGIN: Net