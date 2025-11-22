import typing as T
from pathlib import Path as PathlibPath
import datetime
from pydash import method
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    __convert, __data, __factory, __validate, __inspect
)

Convert = __convert()
Data = __data()
Factory = __factory()
Validate = __validate()

def dump(*args, **kwargs):
    import rich, rich.pretty, rich.console
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

def product(*args, **kwargs):
    from itertools import product
    return product(*args, **kwargs)

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
### END: Net

### BEGIN: Date Time
def datetime_add_or_remove_timezone(
    timestamp: datetime.datetime, *, with_timezone: bool
) -> datetime.datetime:
    return (
        Helper.ensure_utc_timezone(timestamp) if with_timezone else Helper.remove_timezone(timestamp)
    )
### END: Date Time

### BEGIN: Crypto
def crypto_convert_relative_to_datetime(
    relative_time_string: str,
    *,
    with_timezone: bool = False,
    now: datetime.datetime | None = None,
) -> datetime.datetime | None:
    import re
    parsed_result = re.match(
        r"^(?P<prefix>[+-])((?P<weeks>\d+)[wW])?((?P<days>\d+)[dD])?((?P<hours>\d+)[hH])?((?P<minutes>\d+)[mM])?((?P<seconds>\d+)[sS]?)?$",
        relative_time_string,
    )

    if parsed_result is None or len(relative_time_string) == 1:
        # not matched or only a single "+" or "-"
        return None

    offset = datetime.timedelta(0)
    if parsed_result.group("weeks") is not None:
        offset += datetime.timedelta(weeks=int(parsed_result.group("weeks")))
    if parsed_result.group("days") is not None:
        offset += datetime.timedelta(days=int(parsed_result.group("days")))
    if parsed_result.group("hours") is not None:
        offset += datetime.timedelta(hours=int(parsed_result.group("hours")))
    if parsed_result.group("minutes") is not None:
        offset += datetime.timedelta(minutes=int(parsed_result.group("minutes")))
    if parsed_result.group("seconds") is not None:
        offset += datetime.timedelta(seconds=int(parsed_result.group("seconds")))

    if now is None:
        now = Factory.ts() #type: ignore
    else:
        now = datetime_add_or_remove_timezone(now, with_timezone=with_timezone)

    if parsed_result.group("prefix") == "+":
        return now + offset #type: ignore
    return now - offset #type: ignore

def crypto_get_relative_time_option(
    input_string: str,
    *,
    input_name: str,
    with_timezone: bool = False,
    now: datetime.datetime | None = None,
) -> datetime.datetime:
    """
    Return an absolute timespec if a relative timespec or an ASN1 formatted
    string is provided.

    The return value will be a datetime object.
    """
    result = Convert.to_text(input_string)
    if result is None:
        raise ValueError(
            f'The timespec "{input_string}" for {input_name} is not valid'
        )
    # Relative time
    if result.startswith("+") or result.startswith("-"):
        res = crypto_convert_relative_to_datetime(result, with_timezone=with_timezone, now=now)
        if res is None:
            raise ValueError(
                f'The timespec "{input_string}" for {input_name} is invalid'
            )
        return res
    # Absolute time
    for date_fmt, length in [
        (
            "%Y%m%d%H%M%SZ",
            15,
        ),  # this also parses '202401020304Z', but as datetime(2024, 1, 2, 3, 0, 4)
        ("%Y%m%d%H%MZ", 13),
        (
            "%Y%m%d%H%M%S%z",
            14 + 5,
        ),  # this also parses '202401020304+0000', but as datetime(2024, 1, 2, 3, 0, 4, tzinfo=...)
        ("%Y%m%d%H%M%z", 12 + 5),
    ]:
        if len(result) != length:
            continue
        try:
            res = datetime.datetime.strptime(result, date_fmt)
        except ValueError:
            pass
        else:
            return datetime_add_or_remove_timezone(res, with_timezone=with_timezone)

    raise ValueError(
        f'The time spec "{input_string}" for {input_name} is invalid'
    )
### END: Crypto