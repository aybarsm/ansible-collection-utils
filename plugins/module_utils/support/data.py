import typing as t
import functools
from ansible_collections.aybarsm.utils.plugins.module_utils.support.types import (
    T, ENUMERATABLE
)
from ansible_collections.aybarsm.utils.plugins.module_utils.aggregator import Kit

### BEGIN: Arrays
@functools.wraps(Kit.Pydash().chunk)
def chunk(data, size: int = 1) -> t.List[t.Sequence[t.Any]]:
    return Kit.Pydash().chunk(data, size)

@functools.wraps(Kit.Pydash().compact)
def compact(data) -> t.List[t.Any]:
    return Kit.Pydash().compact(data)

@functools.wraps(Kit.Pydash().concat)
def concat(*data) -> t.List[t.Any]:
    return Kit.Pydash().concat(*data)
### END: Arrays

### BEGIN: Locate
@functools.wraps(Kit.Pydash().find)
def find(data, predicate) -> t.Any:
    return Kit.Pydash().find(data, predicate)

@functools.wraps(Kit.Pydash().find_last)
def find_last(data, predicate) -> t.Any:
    return Kit.Pydash().find_last(data, predicate)

@functools.wraps(Kit.Pydash().find_key)
def find_key(data, predicate) -> t.Any:
    return Kit.Pydash().find_key(data, predicate)

@functools.wraps(Kit.Pydash().find_last_key)
def find_last_key(data, predicate) -> t.Any:
    return Kit.Pydash().find_last_key(data, predicate)

@functools.wraps(Kit.Pydash().find_index)
def find_index(data, predicate) -> t.Any:
    return Kit.Pydash().find_index(data, predicate)

@functools.wraps(Kit.Pydash().find_last_index)
def find_last_index(data, predicate) -> t.Any:
    return Kit.Pydash().find_last_index(data, predicate)
### END: Locate

@functools.wraps(Kit.Pydash().get)
def get(data, key, default = None) -> t.Any:
    if not str(key) == '*' and not Kit.Validate().str_contains(str(key), '.*', '*.'):
        return Kit.Pydash().get(data, key, default)
    
    skip_ = []
    ret = Kit.Convert().as_copied(data)
    segments = str(key).strip('.').split('.')
    for idx_, segment in enumerate(segments):
        if idx_ in skip_:
            continue
        
        if segment == '*' and len(segments) > 1 and idx_ < len(segments) - 1 and segments[idx_ + 1] != '*' and Kit.Validate().is_iterable_of_not_mappings(ret):
            _flatten = flatten(ret, levels=1)
            if Kit.Validate().is_iterable_of_mappings(_flatten):
                ret = _flatten

            ret = pluck(ret, segments[idx_ + 1])
            skip_.append(idx_ + 1)
        elif segment == '*' and Kit.Validate().is_mapping(ret):
            ret = list(dict(ret).values())
        elif segment != '*' and Kit.Validate().is_iterable_of_mappings(ret):
            ret = pluck(ret, segment)
        elif segment != '*' and Kit.Validate().is_mapping(ret):
            ret = Kit.Convert().as_copied(Kit.Pydash().get(ret, segment))       
        elif segment == '*':
            ret = flatten(ret, levels=1)
        
        if idx_ <= len(segments) - 1 and not Kit.Validate().is_iterable(ret):
            ret = default
            break

    return ret

@functools.wraps(Kit.Pydash().set_)
def set_(data, key, value: t.Any) -> t.Any:
    return Kit.Pydash().set_(data, key, value)

@functools.wraps(Kit.Pydash().has)
def has(data, key) -> bool:
    return Kit.Pydash().has(data, key)

@functools.wraps(Kit.Pydash().unset)
def unset(data, *args) -> t.Any:
    for key_ in args:
        Kit.Pydash().unset(data, key_)
    
    return data

@functools.wraps(Kit.Pydash().pluck)
def pluck(data, key, **kwargs) -> t.List[t.Any]:
    ph = Kit.Factory().placeholder()
    is_filled = kwargs.pop('filled', ph) != ph
    is_unique = kwargs.pop('unique', ph)

    ret = Kit.Pydash().pluck(data, key)
    if is_filled:
        ret = [item for item in ret if Kit.Validate().filled(item)]
    
    if is_unique != ph:
        ret = uniq(ret, is_unique)
    
    return ret  
    
@functools.wraps(Kit.Pydash().uniq)
def uniq(
    data: ENUMERATABLE[T],
    by: t.Optional[t.Union[t.Literal[True], str, ENUMERATABLE[str], t.Callable]] = None,
) -> list[T]:
    ret = []
    seen = set()

    for key, value in enumerate(data):
        hash_ = Kit.Convert().as_hash(key, value, by)
        if hash_ not in seen:
            ret.append(value)
            seen.add(hash_)
    
    return ret

@functools.wraps(Kit.Pydash().invert)
def invert(data) -> t.Any:
    return Kit.Pydash().invert(data)

@functools.wraps(Kit.Pydash().map_)
def walk(data, iteratee):
    return Kit.Pydash().collections.map_(data, iteratee)

@functools.wraps(Kit.Pydash().map_values_deep)
def walk_values_deep(data, iteratee):
    return Kit.Pydash().map_values_deep(data, iteratee)

@functools.wraps(Kit.Pydash().difference)
def difference(data, *others, **kwargs)-> t.List[t.Any]:
    if Kit.Validate().blank(kwargs):
        return Kit.Pydash().difference_with(data, *others)
    else:
        return Kit.Pydash().difference_by(data, *others, **kwargs)

@functools.wraps(Kit.Pydash().intersection)
def intersection(data, *others, **kwargs)-> t.List[t.Any]:
    if Kit.Validate().blank(kwargs):
        return Kit.Pydash().intersection_with(data, *others)
    else:
        return Kit.Pydash().intersection_by(data, *others, **kwargs)

def _append_or_prepend(data: t.Iterable[t.Any], key: str, value: t.Any, is_prepend: bool, **kwargs) -> t.Iterable[t.Any]:
    is_extend = kwargs.pop('extend', False)
    is_unique = kwargs.pop('unique', False)
    is_sorted = kwargs.pop('sort', False)
    
    if Kit.Validate().is_mapping(data) or Kit.Validate().filled(key):
        current = Kit.Convert().as_copied(list(get(data, key, [])))
    else:
        current = Kit.Convert().as_copied(list(data))
    
    for item in Kit.Convert().to_iterable(value):
        if is_prepend:
            current.insert(0, item)
        else:
            current.append(item)

        if not is_extend:
            break
    
    if is_unique:
        current = list(set(current))
    
    if is_sorted:
        current = list(sorted(current))
        
    if Kit.Validate().is_mapping(data) or Kit.Validate().filled(key):
        set_(data, key, current)
    else:
        data = current
    
    return data

def append(data: t.Iterable[t.Any], key: str, value: t.Any, **kwargs) -> t.Iterable[t.Any]:
    return _append_or_prepend(data, key, value, False, **kwargs)

def prepend(data: t.Iterable[t.Any], key: str, value: t.Any, **kwargs) -> t.Iterable[t.Any]:
    return _append_or_prepend(data, key, value, True, **kwargs)

def dot(data: t.Union[t.Sequence[t.Any], t.Mapping[t.Any, t.Any]], prepend='', **kwargs)-> dict:
    is_main = Kit.Validate().blank(prepend)
    is_main_mapping = is_main and Kit.Validate().is_mapping(data)
    if is_main_mapping:
        data = undot(data) #type: ignore

    ret = {}
    if Kit.Validate().is_sequence(data):
        for key, value in enumerate(data):
            new_key = f"{prepend}{str(key)}"
            if value and (Kit.Validate().is_mapping(value) or Kit.Validate().is_sequence(value)):
                ret.update(dot(value, new_key + '.'))
            else:
                ret[new_key] = value
    elif Kit.Validate().is_mapping(data):
        for key, value in data.items(): #type: ignore
            new_key = f"{prepend}{key}"
            if value and (Kit.Validate().is_mapping(value) or Kit.Validate().is_sequence(value)):
                ret.update(dot(value, new_key + '.'))
            else:
                ret[new_key] = value
    
    if is_main_mapping:
        sorted = kwargs.pop('sorted', False)
        if sorted:
            asc = kwargs.pop('asc', True)
            ret = dict(sorted(ret.items()) if asc else reversed(sorted(ret.items())))
    
    return ret

def undot(data: t.Mapping)-> dict:
    import re
    data = dict(data)
    if Kit.Validate().blank(data):
        return data
    
    done = []
    ret = {}
    for key, value in data.items():
        if key in done:
            continue
        
        done_iter = [key]
        if Kit.Validate().is_mapping(value):
            set_(ret, key, undot(value))
        elif '.' not in str(key):
            ret[key] = value
        elif Kit.Validate().str_is_int(Kit.Str().after_last(key, '.')):
            primary = Kit.Str().before_last(key, '.')
            pattern = '^' + re.escape(primary) + '\\.(\\d+)$'
            pattern = re.compile(pattern)
            seq_keys = [seq_key for seq_key in data.keys() if seq_key not in done and pattern.match(seq_key)]
            seq_keys.sort()
            seq = []
            for seq_key in seq_keys:
                seq.append(data[seq_key])
            done_iter = seq_keys.copy()
            set_(ret, primary, seq.copy())
        else:
            set_(ret, key, value)
        
        done.extend(done_iter)
    
    return ret

def sort_keys_char_count(
    data: t.Iterable[t.Any],
    char: str,
    **kwargs
)-> dict|list:
    
    asc = kwargs.pop('asc', True)
    raw = kwargs.pop('raw', False)
    if Kit.Validate().is_mapping(data):
        ret = sorted(dict(data).items(), key=lambda item: item[0].count(char)) #type: ignore
    else:
        ret = sorted([item for item in list(data)], key=lambda s: s.count(char))

    if not asc:
        ret = reversed(ret)
    
    if raw:
        return ret #type: ignore
    
    if Kit.Validate().is_mapping(data):
        return dict(ret) #type: ignore
    else:
        return list(ret)

def dot_sort_keys(
    data: t.Iterable[t.Any],
    **kwargs
)-> dict|list:
    return sort_keys_char_count(data, '.', **kwargs)

def filled(data: t.Iterable[t.Any], key: str, **kwargs) -> bool:
    return Kit.Validate().filled(get(data, key, **kwargs))

def blank(data: t.Iterable[t.Any], key: str, **kwargs) -> bool:
    return Kit.Validate().blank(get(data, key, **kwargs))

def where(
    data: t.Iterable[t.Any], 
    callback: t.Optional[t.Union[t.Callable, t.Mapping[str, t.Any]]] = None, 
    default: t.Any = None, 
    **kwargs: t.Mapping[str, bool],
) -> t.Any:
    is_negate = kwargs.pop('negate', False)
    is_first = kwargs.pop('first', False)
    is_last = kwargs.pop('last', False)
    is_key = kwargs.pop('key', False)
    is_no_dot = kwargs.pop('no_dot', False)
    is_filled = kwargs.pop('filled', False)
    is_blank = kwargs.pop('blank', False)

    if is_first and is_last:
        raise ValueError('First and last cannot be searched at the same time.')
    
    if is_filled and is_blank:
        raise ValueError('Filled and blank cannot be searched at the same time.')

    if Kit.Validate().blank(data):
        return default
    
    is_mapping = Kit.Validate().is_mapping(data)
    data = Kit.Convert().to_iterable(data)    
    
    if Kit.Validate().is_mapping(callback):
        callback = Kit.Convert().from_mapping_to_callable(dict(callback), **kwargs) #type: ignore
    
    if is_first and not callback:
        if not is_mapping:
            return data[0]
        else:
           return data[list(data[0].keys())[0]]
    
    ret = []

    for key_, val_ in data[0].items() if is_mapping else enumerate(data):
        res = Kit.Utils().call(callback, val_, key_) #type: ignore
        if is_negate:
            res = not res
        
        if res != True:
            continue
        
        if is_key:
            ret.append(key_)
        elif not is_mapping:
            ret.append(val_)
        else:
            if Kit.Validate().blank(ret):
                ret.append({})
            
            ret[0][key_] = val_
        
        if is_first:
            break

    if Kit.Validate().blank(ret):
        return default
    
    if is_first or is_last:
        if is_mapping and not is_key:
            keys_ = list(ret[0].keys())
            return ret[0][keys_[0]] if is_first else ret[0][keys_[-1]]
        else:
            return ret[0] if is_first else ret[-1]
    elif is_mapping:
        return ret[0]

    return ret

def reject(
    data: t.Iterable[t.Any], 
    callback: t.Optional[t.Union[t.Callable, t.Mapping[str, t.Any]]] = None, 
    default: t.Any = None, 
    **kwargs,
)-> t.Any:
    kwargs['negate'] = True
    return where(data, callback, default, **kwargs)

def first(
    data: t.Iterable[t.Any], 
    callback: t.Optional[t.Union[t.Callable, t.Mapping[str, t.Any]]] = None, 
    default: t.Any = None, 
    **kwargs,
)-> t.Any:
    kwargs['first'] = True
    kwargs['last'] = False
    return where(data, callback, default, **kwargs)

def last(
    data: t.Iterable[t.Any], 
    callback: t.Optional[t.Union[t.Callable, t.Mapping[str, t.Any]]] = None, 
    default: t.Any = None, 
    **kwargs,
)-> t.Any:
    kwargs['first'] = False
    kwargs['last'] = True
    return where(data, callback, default, **kwargs)

def first_filled(*args: t.Any, default: t.Any = None)-> t.Any:
    for data in args:
        if Kit.Validate().filled(data):
            return data
    
    return default

def only_with(
    data: t.Iterable[t.Any],
    *args: str,
    **kwargs,
)-> dict[str, t.Any]|list[dict[str, t.Any]]:
    is_meta = kwargs.pop('meta', False)
    is_meta_fix = kwargs.pop('meta_fix', False)
    is_no_dot = kwargs.pop('no_dot', False)
    is_filled = kwargs.pop('filled', False)

    ph = Kit.Factory().placeholder(mod='hashed')
    default_missing = kwargs.pop('default_missing', ph)
    default_blank = kwargs.pop('default_blank', ph)

    is_mapping = Kit.Validate().is_mapping(data)
    data = Kit.Convert().to_pydash(data)
    
    ret = []
    for item in Kit.Convert().to_iterable(data):
        keys = Kit.Convert().as_copied(list(args))
        
        meta_keys = [meta_key for meta_key in item.keys() if str(meta_key).startswith('_')] if is_meta else []
        if Kit.Validate().filled(meta_keys):
            keys.extend(meta_keys)

        new_item = {}
        for key in keys:
            key_exists = (is_no_dot and key in item) or (not is_no_dot and has(item, key))
            
            new_value = item.get(key) if is_no_dot else get(item, key)
            if not key_exists:
                if default_missing != ph:
                    new_value = default_missing
                else:
                    continue
            
            is_value_filled = not is_filled or ((is_no_dot and Kit.Validate().filled(item[key])) or (not is_no_dot and Kit.Validate().filled(get(item, key))))
            if not is_value_filled:
                if default_blank != ph:
                    new_value = default_blank
                else:
                    continue
            
            is_key_meta = is_meta and str(key).startswith('_')
            new_key = str(key).lstrip('_') if is_key_meta and is_meta_fix else key
            
            if is_no_dot:
                new_item[new_key] = Kit.Convert().as_copied(new_value)
            else:
                set_(new_item, new_key, Kit.Convert().as_copied(new_value))
        
        ret.append(new_item)
    
    return ret[0] if is_mapping else ret

def all_except(
    data: t.Iterable[t.Any],
    *args: str,
    **kwargs,
)-> dict[str, t.Any]|list[dict[str, t.Any]]:
    is_meta = kwargs.pop('meta', False)
    is_omitted = kwargs.pop('omitted', False)
    is_no_dot = kwargs.pop('no_dot', False)
    is_blank = kwargs.pop('blank', False)

    is_mapping = Kit.Validate().is_mapping(data)
    data = Kit.Convert().to_pydash(data)
    ret = []

    for item in Kit.Convert().to_iterable(data):
        keys = list(args)
        
        exclude_keys = [exc_key for exc_key in item.keys() if str(exc_key).startswith('_')] if is_meta else []
        if Kit.Validate().filled(exclude_keys):
            keys.extend(exclude_keys)
        
        if is_omitted or is_blank:
            exclude_value_keys = [exc_key for exc_key, exc_value in item.items() if (is_omitted and Kit.Validate().is_ansible_omitted(exc_value)) or (is_blank and Kit.Validate().blank(exc_value))]
        else:
            exclude_value_keys = []
        
        if Kit.Validate().filled(exclude_value_keys):
            keys.extend(exclude_value_keys)

        new_item = Kit.Convert().as_copied(item)
        
        for key in keys:
            key_exists = (is_no_dot and key in item) or (not is_no_dot and has(item, key))
            if not key_exists:
                continue
            
            if is_no_dot:
                del new_item[key]
            else:
                unset(new_item, key)
        
        ret.append(new_item)
    
    return ret[0] if is_mapping else ret

def flatten(data, levels=None, skip_nulls=True):
    ret = []
    for element in data:
        if skip_nulls and element in (None, 'None', 'null'):
            continue
        elif Kit.Validate().is_sequence(element):
            if levels is None:
                ret.extend(flatten(element, skip_nulls=skip_nulls))
            elif levels >= 1:
                ret.extend(flatten(element, levels=(int(levels) - 1), skip_nulls=skip_nulls))
            else:
                ret.append(element)
        else:
            ret.append(element)

    return ret

def merge_hash(x, y, recursive=True, list_merge='replace'):
    Kit.Validate().require_mutable_mappings(x, y)
    
    if x == {} or x == y:
        return y.copy()
    if y == {}:
        return x

    x = x.copy()

    if not recursive and list_merge == 'replace':
        x.update(y)
        return x

    for key, y_value in y.items():
        if key not in x:
            x[key] = y_value
            continue

        x_value = x[key]

        if isinstance(x_value, t.MutableMapping) and isinstance(y_value, t.MutableMapping):
            if recursive:
                x[key] = merge_hash(x_value, y_value, recursive, list_merge)
            else:
                x[key] = y_value
            continue

        if isinstance(x_value, t.MutableSequence) and isinstance(y_value, t.MutableSequence):
            if list_merge == 'replace':
                x[key] = y_value
            elif list_merge == 'append':
                x[key] = x_value + y_value #type: ignore
            elif list_merge == 'prepend':
                x[key] = y_value + x_value #type: ignore
            elif list_merge == 'append_rp':
                x[key] = [z for z in x_value if z not in y_value] + y_value #type: ignore
            elif list_merge == 'prepend_rp':
                x[key] = y_value + [z for z in x_value if z not in y_value] #type: ignore
            continue

        x[key] = y_value

    return x

def combine(*args, **kwargs):
    recursive = kwargs.pop('recursive', False)
    list_merge = kwargs.pop('list_merge', 'replace')
    reverse = kwargs.pop('reverse', False)

    args = list(args)
    if reverse:
        args.reverse()

    dicts = flatten(args, levels=1)

    if Kit.Validate().blank(dicts):
        return {}

    if len(dicts) == 1:
        return dicts[0]

    dicts = reversed(dicts)
    result = next(dicts)
    for dictionary in dicts:
        result = merge_hash(dictionary, result, recursive, list_merge)

    return result

def combine_match(
    data: str,
    items: t.Mapping[str, t.Any] | ENUMERATABLE[t.Mapping[str, t.Any]], 
    attribute: str,
    *args, 
    **kwargs
):
    import re
    is_prepare = kwargs.pop('prepare', False)
    ret = []

    for item in Kit.Convert().to_iterable(items):
        pattern = get(item, attribute)
        if not Kit.Validate().is_string(pattern) or Kit.Validate().blank(pattern):
            continue
            
        if is_prepare:
            pattern = Kit.Str().wrap(pattern, '^', '$')
            
        if re.match(rf"{pattern}", data):
            ret.append(item)
    
    if Kit.Validate().filled(args):
        ret.extend(list(args))
    
    ret = [Kit.Convert().to_safe_json(item) if Kit.Validate().is_ansible_mapping(item) else item for item in ret]

    return combine(*ret, **kwargs)

def map(
    data: ENUMERATABLE[t.Any], 
    callback: t.Callable, 
)-> list:
    return [Kit.Utils().call(callback, val_, key_) for key_, val_ in enumerate(data)]

def keys(
    data: t.Iterable[t.Any],
    **kwargs
)-> t.Any:
    ret = []
    is_mapping = Kit.Validate().is_mapping(data)
    replace = kwargs.pop('replace', {})
    
    no_dot = kwargs.pop('no_dot', False)
    ph = Kit.Factory().placeholder(mod='hashed')

    for item in Kit.Convert().to_iterable(data):
        item_new = Kit.Convert().as_copied(item)
    
        for replacement in replace.get('keys', []):
            if not Kit.Validate().is_sequence(replacement) or len(replacement) < 2:
                raise ValueError('Key replacement requires at least 2 elements')
        
            key_from = replacement[0]
            key_to = replacement[1]
            if key_from == key_to:
                continue

            key_default = ph
            key_exists = (no_dot and key_from in item_new) or (not no_dot and has(item_new, key_from))

            if len(replacement) > 2:
                key_default = replacement[2]

            value_new = key_default
            if key_exists and no_dot:
                value_new = item_new[key_from]
            elif key_exists and not no_dot:
                value_new = get(item_new, key_from)
            
            if value_new == ph:
                continue

            if no_dot:
                item_new[key_to] = value_new
            else:
                set_(item_new, key_to, value_new)

            if key_exists and not Kit.Validate().is_falsy(replace.get('remove_replaced', True)):
                if no_dot:
                    del item_new[key_from]
                else:
                    unset(item_new, key_from)
            
        ret.append(item_new)

    return ret[0] if is_mapping else ret

# BEGIN: Aliases
forget: t.Callable = unset
flip: t.Callable = invert
unique: t.Callable = uniq
unique_by: t.Callable = uniq
difference_with: t.Callable = intersection
difference_by: t.Callable = intersection
intersect: t.Callable = intersection
intersect_with: t.Callable = intersection
intersect_by: t.Callable = intersection

select = t.Callable = where
# END: Aliases