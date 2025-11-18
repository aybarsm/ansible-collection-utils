import typing as T
from pathlib import Path as PathlibPath
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    __validate, __inspect
)

def dump(*args, **kwargs):
    import rich, rich.pretty
    if __validate().is_ansible_env():
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

#BEGIN: Json
def json_parse(data: str, **kwargs)-> dict|list:
    import json
    return json.loads(data, **kwargs)

def json_dump(
    data: T.Union[T.Sequence[T.Any], T.Mapping[T.Any, T.Any]], 
    **kwargs,
)-> str:
    import json
    return json.dumps(data, **kwargs)
#END: Json

#BEGIN: Yaml
@staticmethod
def yaml_parse(data: str)-> dict|list:
    import yaml
    return yaml.unsafe_load(data)

def yaml_dump(
    data: T.Union[T.Sequence[T.Any], T.Mapping[T.Any, T.Any]], 
    **kwargs,
)-> str:
    import yaml
    return yaml.dump(data, **kwargs)
#END: Yaml

#BEGIN: Callable
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
#END: Callable

#BEGIN: FS
def fs_dirname(path: T.Union[PathlibPath, str])-> str:
    return str(PathlibPath(path).parent)
#END: FS