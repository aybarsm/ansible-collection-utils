### BEGIN: Imports
import typing as t
from pathlib import Path as PathlibPath
import datetime, asyncio
### END: Imports
### BEGIN: ImportManager
from ansible_collections.aybarsm.utils.plugins.module_utils.support.ansible import (
	Ansible_display,
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.convert import (
	Convert_as_callable_segments, Convert_as_ip_address, Convert_from_json,
	Convert_from_yaml, Convert_to_json, Convert_to_text,
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.data import (
	Data_all_except, Data_filled, Data_get,
	Data_only_with,
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.factory import (
	Factory_ts,
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.validate import (
	Validate_blank, Validate_callable_is_coroutine, Validate_filled,
	Validate_is_ansible_env, Validate_is_ip_private, Validate_is_ip_public,
	Validate_is_ip_v4, Validate_is_ip_v6, Validate_is_mapping,
	Validate_is_object, Validate_is_sequence, Validate_is_string,
)
### END: ImportManager

def Utils_dump(*args, **kwargs):
    separator = kwargs.pop('separator', None)
    separator = separator if isinstance(separator, Definitions_Separator) else None
    
    if separator:
        new_args = []
        for idx, arg in enumerate(args):
            if idx == len(args) - 1:
                new_args.append(arg.make() if isinstance(arg, Definitions_Separator) else arg)
                break
            
            if isinstance(arg, Definitions_Separator):
                new_args.append(arg.make())
                continue

            new_args.extend([arg, separator.make()])
        
        args=new_args

    if Validate_is_ansible_env():
        import io
        buffer = io.StringIO()
        console = RichConsole_Console(file=buffer, force_terminal=False)
        for arg in args:
            console.print(RichPretty_Pretty(arg, **kwargs))

        Ansible_display().display(buffer.getvalue())
    else:
        for arg in args:
            RichPretty_pprint(arg, **kwargs)

def Utils_dd(*args, **kwargs):
    Utils_dump(*args, **kwargs)
    exit(0)

def Utils_product(*args, **kwargs):
    from itertools import product
    return Utils_product(*args, **kwargs)

### BEGIN: Json
def Utils_json_load(path: PathlibPath|str, **kwargs)-> dict|list:
    return Convert_from_json(Utils_fs_read(path), **kwargs)

def Utils_json_save(data, path: PathlibPath|str, **kwargs) -> None:
        path = PathlibPath(path)
        overwrite = kwargs.pop('overwrite', False)

        if path.exists() and not overwrite:
            raise ValueError(f'Json file [{str(path)}] already exists.')
        
        kwargs_path = Data_only_with(kwargs, 'encoding', 'errors')
        kwargs_json = Data_all_except(kwargs, 'encoding', 'errors', 'newline')
        
        data = Convert_from_yaml(Convert_to_text(data))

        if Validate_is_mapping(data):
            data = Convert_to_json(dict(data), **kwargs_json) #type: ignore
        elif Validate_is_sequence(data):
            data = Convert_to_json(list(data), **kwargs_json) #type: ignore
        
        Utils_fs_write(path, str(data), **kwargs_path) #type: ignore
### END: Json

### BEGIN: Callable
def Utils_call_raw(callback: t.Callable, *args, **kwargs) -> t.Any:
    if Validate_blank(args) and Validate_blank(kwargs):
        return callback()
    
    conf = dict(kwargs.pop('__caller', {}))
    segments = Convert_as_callable_segments(callback)
    args = list(args)
    kwargs = dict(kwargs)
    send_args = []
    send_kwargs = {}
    
    if Data_filled(conf, 'bind.annotations'):
        if 'annotation' not in conf['bind']:
            conf['bind']['annotation'] = {}
        
        for binding_ in Data_get(conf, 'bind.annotations', []):
            if type(binding_) not in conf['bind']['annotation']:
                conf['bind']['annotation'][type(binding_)] = binding_

        del conf['bind']['annotations']
    
    for param in segments['params']:
        if param['has']['annotation'] and param['annotation'] in Data_get(conf, 'bind.annotation', {}):
            bound = conf['bind']['annotation'][param['annotation']]
            del conf['bind']['annotation'][param['annotation']]
            
            if param['type'] == 'pos':
                send_args.insert(param['pos'], bound)
            else:
                send_kwargs[param['name']] = bound
        elif param['type'] == 'pos' and len(send_args) < segments['has']['params']['pos'] and Validate_filled(args):
            send_args.append(args[0])
            del args[0]
        elif param['type'] == 'any' and param['name'] not in kwargs and Validate_filled(args):
            send_kwargs[param['name']] = args[0]
            del args[0]
        elif param['type'] in ['any', 'key'] and param['name'] in kwargs:
            send_kwargs[param['name']] = kwargs.pop(param['name'])
        elif param['type'] == 'args':
            if Validate_filled(args):
                send_args.extend(args)
            args = []
        elif param['type'] == 'kwargs':
            for key_ in kwargs.keys():
                if key_ not in send_kwargs:
                    send_kwargs[key_] = kwargs[key_]
                
            kwargs = {}

    return callback(*send_args, **send_kwargs)

def Utils_call(callback: t.Callable, *args, **kwargs) -> t.Any:
    return Utils_call_raw(callback, *args, **kwargs)

async def Utils_call_async(callback: t.Callable, *args, **kwargs) -> t.Any:
    return await Utils_call_raw(callback, *args, **kwargs)

# def Utils_call(callback: t.Callable, *args, **kwargs) -> t.Any:
#     result = Utils_call_raw(callback, *args, **kwargs)
#     if asyncio.iscoroutine(result):
#         try:
#             asyncio.get_running_loop()
#         except RuntimeError:
#             return asyncio.run(result)
#         else:
#             raise RuntimeError("Async code detected in sync call while event loop is running in this thread.")
#     return result

# async def call_async(callback: t.Callable, *args, **kwargs) -> t.Any:
#     result = Utils_call_raw(callback, *args, **kwargs)
#     if asyncio.iscoroutine(result):
#         return await result
#     return result

async def Utils_call_semaphore(semaphore: asyncio.Semaphore, callback: t.Callable, *args, **kwargs) -> t.Any:
    async with semaphore:
        if Validate_callable_is_coroutine(callback):
            result = await Utils_call_raw(callback, *args, **kwargs)
        else:
            result = await asyncio.get_running_loop().run_in_executor(None, lambda: Utils_call_raw(callback, *args, **kwargs))
    
        return result

def Utils_tap_(value: t.Any, callback: t.Callable) -> t.Any:
    callback(value)
    return value

def Utils_with_(value: t.Any, callback: t.Callable) -> t.Any:
    return callback(value)
### END: Callable

### BEGIN: FS
def Utils_fs_dirname(path: PathlibPath|str)-> str:
    return str(PathlibPath(path).parent)

def Utils_fs_join_paths(*args, **kwargs):
    import os
    normalize = kwargs.pop('normalize', True)
    
    args = list(args)
    for idx in range(0, len(args)):
        args[idx] = str(args[idx]).strip().rstrip(os.sep).strip()

    ret = os.path.join(*args)
    if normalize:
        ret = os.path.normpath(ret)

    return str(ret)

def Utils_fs_ensure_directory_exists(path: PathlibPath|str)-> None:
    PathlibPath(path).mkdir(parents=True, exist_ok=True)

def Utils_fs_read(path: PathlibPath|str, **kwargs)-> str:
    return PathlibPath(path).read_text(**kwargs)

def Utils_fs_read_bytes(path: PathlibPath|str, **kwargs)-> bytes:
    return PathlibPath(path).read_bytes(**kwargs)

def Utils_fs_write(path: PathlibPath|str, data: str|bytes, **kwargs)-> None:
    path = PathlibPath(path)
    if Validate_is_string(data):
        path.write_text(str(data), **kwargs)
    else:
        path.write_bytes(data, **kwargs) #type: ignore

def Utils_fs_top_level_dirs(paths: str|t.Sequence[str], *args: str)-> list[str]:
    import os

    paths = list(paths)
    if Validate_filled(args):
        paths.extend(args)
    
    paths = list(set(paths))

    if Validate_blank(paths):
        return []

    ret = []

    norm_paths = sorted(set(os.path.normpath(p) for p in paths), key=lambda p: p.count(os.sep), reverse=True)
    for path in norm_paths:
        if not any(os.path.commonpath([path, existing]) == path for existing in ret):
            ret.append(path)

    return ret
### END: FS

### BEGIN: Net
def Utils_net_subnets_collapse(data: t.Sequence[str], **kwargs) -> list:
    only = kwargs.pop('only', '')
    proto = kwargs.pop('proto', '')

    only_private = only in ['pri', 'private']
    only_public = only in ['pub', 'public']
    only_v4 = proto in ['4', 'v4', 4]
    only_v6 = proto in ['6', 'v6', 6]
    
    ret = []

    for subnet in data:
        addr = Convert_as_ip_address(subnet)
        
        if (only_private and Validate_is_ip_public(addr)) or (only_public and Validate_is_ip_private(addr)):
            continue

        if (only_v4 and Validate_is_ip_v6(addr)) or (only_v6 and Validate_is_ip_v4(addr)):
            continue

        supernets = list(set(data) - set([subnet]))
        if not any([Validate_is_subnet_of(subnet, supernet) for supernet in supernets]):
            ret.append(subnet)

    return list(set(ret))
### END: Net

### BEGIN: Date Time
def Utils_ensure_utc_timezone(timestamp: datetime.datetime) -> datetime.datetime:
        if timestamp.tzinfo is datetime.timezone.utc:
            return timestamp
        if timestamp.tzinfo is None:
            return timestamp.replace(tzinfo=datetime.timezone.utc)
        return timestamp.astimezone(datetime.timezone.utc)

def Utils_remove_timezone(timestamp: datetime.datetime) -> datetime.datetime:
        # Convert to native datetime object
        if timestamp.tzinfo is None:
            return timestamp
        if timestamp.tzinfo is not datetime.timezone.utc:
            timestamp = timestamp.astimezone(datetime.timezone.utc)
        return timestamp.replace(tzinfo=None)

def Utils_datetime_add_or_remove_timezone(
    timestamp: datetime.datetime, *, with_timezone: bool
) -> datetime.datetime:
    return (
        Utils_ensure_utc_timezone(timestamp) if with_timezone else Utils_remove_timezone(timestamp)
    )
### END: Date Time

### BEGIN: Crypto
def Utils_crypto_convert_relative_to_datetime(
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
        now = Factory_ts() #type: ignore
    else:
        now = Utils_datetime_add_or_remove_timezone(now, with_timezone=with_timezone)

    if parsed_result.group("prefix") == "+":
        return now + offset #type: ignore
    return now - offset #type: ignore

def Utils_crypto_get_relative_time_option(
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
    result = Convert_to_text(input_string)
    if result is None:
        raise ValueError(
            f'The timespec "{input_string}" for {input_name} is not valid'
        )
    # Relative time
    if result.startswith("+") or result.startswith("-"):
        res = Utils_crypto_convert_relative_to_datetime(result, with_timezone=with_timezone, now=now)
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
            return Utils_datetime_add_or_remove_timezone(res, with_timezone=with_timezone)

    raise ValueError(
        f'The time spec "{input_string}" for {input_name} is invalid'
    )
### END: Crypto

### BEGIN: Generic
def Utils_class_get_mro(self_: object):
    return 

def Utils_class_get_primary_child(self_: object, parent: type) -> bool | object:
    if self_.__class__ is parent:
        return True

    mros = type(self_).__mro__
    for idx, mro in enumerate(mros):
        if not Validate_is_object(mro):
            break
        
        if mro is parent:
            return mros[idx - 1]
    
    return False

def Utils_value(context: t.Any, *args, **kwargs):
    return Utils_call_raw(context, *args, **kwargs) if callable(context) else context
    
def Utils_when(condition: t.Any, context: t.Any, default: t.Any = None):
    if callable(condition):
        condition = condition()

    if condition:
        return Utils_value(context, condition)
    else:
        return Utils_value(default, condition)
### END: Generic