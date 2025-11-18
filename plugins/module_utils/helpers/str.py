import typing as T
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    __convert, __factory, __validate
)

Convert = __convert()
Factory = __factory()
Validate = __validate()

### BEGIN: Locate
def find(data: str, needle: str, reverse: bool = False, before: bool = True, **kwargs) -> str:
    ph = Factory.placeholder(mod='hashed')
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

def matches(data: str|T.Sequence[str], patterns: str|T.Sequence[str], **kwargs)-> list[str]:
    return [entry for entry in Convert.to_iterable(data) if Validate.str_is_regex_match(entry, patterns, **kwargs)]
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
    import re
    if double:
        return re.sub(r'(?<!\\)"', r'\"', haystack)
    else:
        return re.sub(r"(?<!\\)'", r"\'", haystack)

def remove_empty_lines(data: str) -> str:
    import re
    return re.sub(r'(\n\s*){2,}', '\n', re.sub(r'^\s*[\r\n]+|[\r\n]+\s*\Z', '', data))
### END: Manipulate

### BEGIN: Cases
def case_snake(data: str) -> str:
    import re
    ret = data.replace('-', ' ')
    ret = re.sub(r'([A-Z]+)', r' \1', ret)
    ret = re.sub(r'([A-Z][a-z]+)', r' \1', ret)
    return '_'.join(ret.split()).lower()
### END: Cases