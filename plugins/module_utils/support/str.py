import typing as t
import re
from ansible_collections.aybarsm.utils.plugins.module_utils.aggregator import Kit

### BEGIN: Locate
def find(data: str, needle: str, reverse: bool = False, before: bool = True, **kwargs) -> str:
    ph = Factory_placeholder(mod='hashed')
    default = str(kwargs.pop('default', ph))

    index = data.rfind(needle) if reverse else data.find(needle)
    ret = str(data if index == -1 else (data[:index] if before else data[index + len(needle):]))
    return default if default != ph and ret == data else ret

def before(data: str, needle: str, **kwargs)-> str:
    return find(data, needle, **kwargs)

def before_last(data: str, needle: str, **kwargs)-> str:
    return find(data, needle, reverse = True, **kwargs)

def after(data: str, needle: str, **kwargs)-> str:
    return find(data, needle, reverse = False, before = False, **kwargs)

def after_last(data: str, needle: str, **kwargs)-> str:
    return find(data, needle, reverse = True, before = False, **kwargs)

def matches(data: str|t.Sequence[str], patterns: str|t.Sequence[str], **kwargs)-> list[str]|str:    
    is_cli = kwargs.get('cli', False) == True
    is_all = kwargs.get('all', False) == True
    is_prepare = kwargs.get('prepare', False) == True
    is_escape_data = kwargs.get('escape_data', False) == True
    is_escape_pattern = kwargs.get('escape_pattern', False) == True
    is_first = kwargs.get('first', False) == True
    
    data = Convert_to_iterable(data)
    patterns = Convert_to_iterable(patterns)
    
    if Validate_blank(patterns):
        return []
    
    if is_cli:
        patterns = Data_flatten(Data_map(
            patterns,
            lambda entry: Convert_from_cli(entry, iterable=True, stripped=True)
        ))
    
    ret = []

    for idx, entry in enumerate(data):
        if is_escape_data:
            entry = re.escape(entry)
        
        for pattern in patterns:
            if is_escape_pattern:
                pattern = re.escape(pattern)
            
            if is_prepare:
                pattern = wrap(pattern, '^', '$')
            
            res = re.match(rf"{pattern}", entry) != None

            if not is_all and res:
                ret.append(data[idx])
                break
            elif is_all and not res:
                break
        
        if is_first and Validate_filled(ret):
            break
    
    if is_first and Validate_filled(ret):
        return ret[0]

    return ret
### END: Locate

### BEGIN: Manipulate
def _start_or_finish(haystack: str, needle: str, start: bool)-> str:
    if haystack.strip() == '' or needle.strip() == '' or (start and haystack.startswith(needle)) or (not start and haystack.endswith(needle)):
        return haystack
    
    return f'{needle}{haystack}' if start else f'{haystack}{needle}'

def start(haystack: str, needle: str)-> str:
    return _start_or_finish(haystack, needle, True)

def finish(haystack: str, needle: str)-> str:
    return _start_or_finish(haystack, needle, False)

def wrap(haystack: str, prefix: str, suffix: str)-> str:
    haystack = start(haystack, prefix)
    return finish(haystack, suffix)

def quote(haystack: str, single: bool = True)-> str:
    return wrap(haystack, ("'" if single else '"'), ("'" if single else '"'))

def chop_both(data: str, *args: str)-> str:
    for n in args:
        data = chop_end(chop_start(data, n), n)
    return data

def chop_start(data: str, *args: str)-> str:
    for n in args:
        if data.startswith(n):
            return data[len(n):]
    return data

def chop_end(data: str, *args: str)-> str:
    for n in args:
        if data.endswith(n):
            return data[:-len(n)]
    return data

def escape_quotes(haystack: str, double: bool = True)-> str:
    if double:
        return re.sub(r'(?<!\\)"', r'\"', haystack)
    else:
        return re.sub(r"(?<!\\)'", r"\'", haystack)

def remove_empty_lines(data: str) -> str:
    return re.sub(r'(\n\s*){2,}', '\n', re.sub(r'^\s*[\r\n]+|[\r\n]+\s*\Z', '', data))

def pad(data: t.Any, count: int = 4, char: str = ' ', **kwargs)-> str:
    padding = kwargs.pop('pad')
    if padding not in ['left', 'right', 'both']:
        raise ValueError(f'Invalid padding type [{padding}]. Available: left, right, both')

    count = max([count, 0])
    data = str(Convert_to_text(data))
    is_strip = kwargs.pop('strip', True)
    is_dent = kwargs.pop('dent', False)

    if not Validate_is_falsy(is_strip):
        data = data.strip()
            
    if Validate_is_truthy(is_dent):
        padding = 'left' if padding == 'right' else ('right' if padding == 'left' else padding)
        count += len(data)
    
    if padding == 'left':
        return str(data).ljust(count, char)
    elif padding == 'right':
        return str(data).rjust(count, char)
    else:
        return str(data).center(count, char)

def ljust(data: t.Any, count: int = 4, char: str = ' ', **kwargs)-> str:
    kwargs['pad'] = 'left'
    return pad(data, count, char, **kwargs)

def rjust(data: t.Any, count: int = 4, char: str = ' ', **kwargs)-> str:
    kwargs['pad'] = 'right'
    return pad(data, count, char, **kwargs)

def center(data: t.Any, count: int = 4, char: str = ' ', **kwargs)-> str:
    kwargs['pad'] = 'both'
    return pad(data, count, char, **kwargs)

def pad_left(data: t.Any, count: int = 4, char: str = ' ', **kwargs)-> str:
    return ljust(data, count, char, **kwargs)

def pad_right(data: t.Any, count: int = 4, char: str = ' ', **kwargs)-> str:
    return rjust(data, count, char, **kwargs)

def pad_both(data: t.Any, count: int = 4, char: str = ' ', **kwargs)-> str:
    return rjust(data, count, char, **kwargs)
### END: Manipulate

### BEGIN: Factory
def repeat(data: str, times: int = 1, as_list: bool = False) -> list[str]|str:
    ret = [data for _ in range(max(times, 1))]
    return ret if as_list else ''.join(ret)
### END: Factory

### BEGIN: Cases
def case_snake(data: str) -> str:
    ret = data.replace('-', ' ')
    ret = re.sub(r'([A-Z]+)', r' \1', ret)
    ret = re.sub(r'([A-Z][a-z]+)', r' \1', ret)
    return '_'.join(ret.split()).lower()
### END: Cases