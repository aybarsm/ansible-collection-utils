from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    __factory
)

#BEGIN: Locate
def find(haystack: str, needle: str, reverse: bool = False, before: bool = True, **kwargs) -> str:
    ph = __factory().placeholder(mod='hashed')
    default = str(kwargs.pop('default', ph))

    index = haystack.rfind(needle) if reverse else haystack.find(needle)
    ret = str(haystack if index == -1 else (haystack[:index] if before else haystack[index + len(needle):]))
    return default if default != ph and ret == haystack else ret

def before(haystack: str, needle: str, **kwargs) -> str:
    return find(haystack, needle, **kwargs)

def before_last(haystack, needle, **kwargs) -> str:
    return find(haystack, needle, reverse = True, **kwargs)

def after(haystack, needle, **kwargs) -> str:
    return find(haystack, needle, reverse = False, before = False, **kwargs)

def after_last(haystack, needle, **kwargs) -> str:
    return find(haystack, needle, reverse = True, before = False, **kwargs)
#END: Locate

#BEGIN: Manipulate
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
#END: Manipulate

#BEGIN: Cases
def case_snake(data: str) -> str:
    import re
    ret = data.replace('-', ' ')
    ret = re.sub(r'([A-Z]+)', r' \1', ret)
    ret = re.sub(r'([A-Z][a-z]+)', r' \1', ret)
    return '_'.join(ret.split()).lower()
#END: Cases