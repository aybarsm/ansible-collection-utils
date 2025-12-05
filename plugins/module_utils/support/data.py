### BEGIN: Imports
import typing as t
import functools
### END: Imports
### BEGIN: ImportManager
from ansible_collections.aybarsm.utils.plugins.module_utils.support.convert import (
	Convert_as_copied, Convert_as_hash, Convert_from_mapping_to_callable,
	Convert_to_iterable, Convert_to_pydash,
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.str import (
	Str_after_last, Str_before_last, Str_wrap,
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.utils import (
	Utils_call,
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.validate import (
	Validate_blank, Validate_filled, Validate_is_ansible_mapping,
	Validate_is_ansible_omitted, Validate_is_falsy, Validate_is_iterable,
	Validate_is_iterable_of_mappings, Validate_is_iterable_of_not_mappings, Validate_is_mapping,
	Validate_is_sequence, Validate_is_string, Validate_require_mutable_mappings,
	Validate_str_contains, Validate_str_is_int,
)
### END: ImportManager

def Data_pydash():
    import pydash
    return pydash

def Data_arrays():
    return Data_pydash().arrays

def Data_collections():
    return Data_pydash().collections

### BEGIN: Arrays
@functools.wraps(Data_pydash().chunk)
def Data_chunk(data, size: int = 1) -> t.List[t.Sequence[t.Any]]:
    return Data_pydash().chunk(data, size)

@functools.wraps(Data_pydash().compact)
def Data_compact(data) -> t.List[t.Any]:
    return Data_pydash().compact(data)

@functools.wraps(Data_pydash().concat)
def Data_concat(*data) -> t.List[t.Any]:
    return Data_pydash().concat(*data)
### END: Arrays

### BEGIN: Locate
@functools.wraps(Data_pydash().find)
def Data_find(data, predicate) -> t.Any:
    return Data_pydash().find(data, predicate)

@functools.wraps(Data_pydash().find_last)
def Data_find_last(data, predicate) -> t.Any:
    return Data_pydash().find_last(data, predicate)

@functools.wraps(Data_pydash().find_key)
def Data_find_key(data, predicate) -> t.Any:
    return Data_pydash().find_key(data, predicate)

@functools.wraps(Data_pydash().find_last_key)
def Data_find_last_key(data, predicate) -> t.Any:
    return Data_pydash().find_last_key(data, predicate)

@functools.wraps(Data_pydash().find_index)
def Data_find_index(data, predicate) -> t.Any:
    return Data_pydash().find_index(data, predicate)

@functools.wraps(Data_pydash().find_last_index)
def Data_find_last_index(data, predicate) -> t.Any:
    return Data_pydash().find_last_index(data, predicate)
### END: Locate

@functools.wraps(Data_pydash().get)
def Data_get(data, key, default = None) -> t.Any:
    if not str(key) == '*' and not Validate_str_contains(str(key), '.*', '*.'):
        return Data_pydash().get(data, key, default)
    
    skip_ = []
    ret = Convert_as_copied(data)
    segments = str(key).strip('.').split('.')
    for idx_, segment in enumerate(segments):
        if idx_ in skip_:
            continue
        
        if segment == '*' and len(segments) > 1 and idx_ < len(segments) - 1 and segments[idx_ + 1] != '*' and Validate_is_iterable_of_not_mappings(ret):
            _flatten = Data_flatten(ret, levels=1)
            if Validate_is_iterable_of_mappings(_flatten):
                ret = _flatten

            ret = Data_pluck(ret, segments[idx_ + 1])
            skip_.append(idx_ + 1)
        elif segment == '*' and Validate_is_mapping(ret):
            ret = list(dict(ret).values())
        elif segment != '*' and Validate_is_iterable_of_mappings(ret):
            ret = Data_pluck(ret, segment)
        elif segment != '*' and Validate_is_mapping(ret):
            ret = Convert_as_copied(Data_pydash().get(ret, segment))       
        elif segment == '*':
            ret = Data_flatten(ret, levels=1)
        
        if idx_ <= len(segments) - 1 and not Validate_is_iterable(ret):
            ret = default
            break

    return ret

@functools.wraps(Data_pydash().set_)
def Data_set(data, key, value: t.Any) -> t.Any:
    return Data_pydash().set_(data, key, value)

@functools.wraps(Data_pydash().has)
def Data_has(data, key) -> bool:
    return Data_pydash().has(data, key)

@functools.wraps(Data_pydash().unset)
def Data_unset(data, *args) -> t.Any:
    for key_ in args:
        Data_pydash().unset(data, key_)
    
    return data

@functools.wraps(Data_pydash().pluck)
def Data_pluck(data, key, **kwargs) -> t.List[t.Any]:
    ph = Sentinel.hash
    is_filled = kwargs.pop('filled', ph) != ph
    is_unique = kwargs.pop('unique', ph)

    ret = Data_pydash().pluck(data, key)
    if is_filled:
        ret = [item for item in ret if Validate_filled(item)]
    
    if is_unique != ph:
        ret = Data_uniq(ret, is_unique)
    
    return ret  
    
@functools.wraps(Data_pydash().uniq)
def Data_uniq(
    data: ENUMERATABLE[T],
    by: t.Optional[t.Union[t.Literal[True], str, ENUMERATABLE[str], t.Callable]] = None,
) -> list[T]:
    ret = []
    seen = set()

    for key, value in enumerate(data):
        hash_ = Convert_as_hash(key, value, by)
        if hash_ not in seen:
            ret.append(value)
            seen.add(hash_)
    
    return ret

@functools.wraps(Data_pydash().invert)
def Data_invert(data) -> t.Any:
    return Data_pydash().invert(data)

@functools.wraps(Data_pydash().map_)
def Data_walk(data, iteratee):
    return Data_pydash().collections.map_(data, iteratee)

@functools.wraps(Data_pydash().map_values_deep)
def Data_walk_values_deep(data, iteratee):
    return Data_pydash().map_values_deep(data, iteratee)

@functools.wraps(Data_pydash().difference)
def Data_difference(data, *others, **kwargs)-> t.List[t.Any]:
    if Validate_blank(kwargs):
        return Data_pydash().difference_with(data, *others)
    else:
        return Data_pydash().difference_by(data, *others, **kwargs)

@functools.wraps(Data_pydash().intersection)
def Data_intersectionion(data, *others, **kwargs)-> t.List[t.Any]:
    if Validate_blank(kwargs):
        return Data_pydash().intersection_with(data, *others)
    else:
        return Data_pydash().intersection_by(data, *others, **kwargs)

def _append_or_prepend(data: t.Iterable[t.Any], key: str, value: t.Any, is_prepend: bool, **kwargs) -> t.Iterable[t.Any]:
    is_extend = kwargs.pop('extend', False)
    is_unique = kwargs.pop('unique', False)
    is_sorted = kwargs.pop('sort', False)
    
    if Validate_is_mapping(data) or Validate_filled(key):
        current = Convert_as_copied(list(Data_get(data, key, [])))
    else:
        current = Convert_as_copied(list(data))
    
    for item in Convert_to_iterable(value):
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
        
    if Validate_is_mapping(data) or Validate_filled(key):
        Data_set(data, key, current)
    else:
        data = current
    
    return data

def Data_append(data: t.Iterable[t.Any], key: str, value: t.Any, **kwargs) -> t.Iterable[t.Any]:
    return _append_or_prepend(data, key, value, False, **kwargs)

def Data_prepend(data: t.Iterable[t.Any], key: str, value: t.Any, **kwargs) -> t.Iterable[t.Any]:
    return _append_or_prepend(data, key, value, True, **kwargs)

def Data_dot(data: t.Union[t.Sequence[t.Any], t.Mapping[t.Any, t.Any]], prepend='', **kwargs)-> dict:
    is_main = Validate_blank(prepend)
    is_main_mapping = is_main and Validate_is_mapping(data)
    if is_main_mapping:
        data = Data_undot(data) #type: ignore

    ret = {}
    if Validate_is_sequence(data):
        for key, value in enumerate(data):
            new_key = f"{prepend}{str(key)}"
            if value and (Validate_is_mapping(value) or Validate_is_sequence(value)):
                ret.update(Data_dot(value, new_key + '.'))
            else:
                ret[new_key] = value
    elif Validate_is_mapping(data):
        for key, value in data.items(): #type: ignore
            new_key = f"{prepend}{key}"
            if value and (Validate_is_mapping(value) or Validate_is_sequence(value)):
                ret.update(Data_dot(value, new_key + '.'))
            else:
                ret[new_key] = value
    
    if is_main_mapping:
        sorted = kwargs.pop('sorted', False)
        if sorted:
            asc = kwargs.pop('asc', True)
            ret = dict(sorted(ret.items()) if asc else reversed(sorted(ret.items())))
    
    return ret

def Data_undot(data: t.Mapping)-> dict:
    import re
    data = dict(data)
    if Validate_blank(data):
        return data
    
    done = []
    ret = {}
    for key, value in data.items():
        if key in done:
            continue
        
        done_iter = [key]
        if Validate_is_mapping(value):
            Data_set(ret, key, Data_undot(value))
        elif '.' not in str(key):
            ret[key] = value
        elif Validate_str_is_int(Str_after_last(key, '.')):
            primary = Str_before_last(key, '.')
            pattern = '^' + re.escape(primary) + '\\.(\\d+)$'
            pattern = re.compile(pattern)
            seq_keys = [seq_key for seq_key in data.keys() if seq_key not in done and pattern.match(seq_key)]
            seq_keys.sort()
            seq = []
            for seq_key in seq_keys:
                seq.append(data[seq_key])
            done_iter = seq_keys.copy()
            Data_set(ret, primary, seq.copy())
        else:
            Data_set(ret, key, value)
        
        done.extend(done_iter)
    
    return ret

def Data_sort_keys_char_count(
    data: t.Iterable[t.Any],
    char: str,
    **kwargs
)-> dict|list:
    
    asc = kwargs.pop('asc', True)
    raw = kwargs.pop('raw', False)
    if Validate_is_mapping(data):
        ret = sorted(dict(data).items(), key=lambda item: item[0].count(char)) #type: ignore
    else:
        ret = sorted([item for item in list(data)], key=lambda s: s.count(char))

    if not asc:
        ret = reversed(ret)
    
    if raw:
        return ret #type: ignore
    
    if Validate_is_mapping(data):
        return dict(ret) #type: ignore
    else:
        return list(ret)

def Data_dot_sort_keys(
    data: t.Iterable[t.Any],
    **kwargs
)-> dict|list:
    return Data_sort_keys_char_count(data, '.', **kwargs)

def Data_filled(data: t.Iterable[t.Any], key: str, **kwargs) -> bool:
    return Validate_filled(Data_get(data, key, **kwargs))

def Data_blank(data: t.Iterable[t.Any], key: str, **kwargs) -> bool:
    return Validate_blank(Data_get(data, key, **kwargs))

def Data_where(
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

    if Validate_blank(data):
        return default
    
    is_mapping = Validate_is_mapping(data)
    data = Convert_to_iterable(data)    
    
    if Validate_is_mapping(callback):
        callback = Convert_from_mapping_to_callable(dict(callback), **kwargs) #type: ignore
    
    if is_first and not callback:
        if not is_mapping:
            return data[0]
        else:
           return data[list(data[0].keys())[0]]
    
    ret = []

    for key_, val_ in data[0].items() if is_mapping else enumerate(data):
        res = Utils_call(callback, val_, key_) #type: ignore
        if is_negate:
            res = not res
        
        if res != True:
            continue
        
        if is_key:
            ret.append(key_)
        elif not is_mapping:
            ret.append(val_)
        else:
            if Validate_blank(ret):
                ret.append({})
            
            ret[0][key_] = val_
        
        if is_first:
            break

    if Validate_blank(ret):
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

def Data_reject(
    data: t.Iterable[t.Any], 
    callback: t.Optional[t.Union[t.Callable, t.Mapping[str, t.Any]]] = None, 
    default: t.Any = None, 
    **kwargs,
)-> t.Any:
    kwargs['negate'] = True
    return Data_where(data, callback, default, **kwargs)

def Data_first(
    data: t.Iterable[t.Any], 
    callback: t.Optional[t.Union[t.Callable, t.Mapping[str, t.Any]]] = None, 
    default: t.Any = None, 
    **kwargs,
)-> t.Any:
    kwargs['first'] = True
    kwargs['last'] = False
    return Data_where(data, callback, default, **kwargs)

def Data_last(
    data: t.Iterable[t.Any], 
    callback: t.Optional[t.Union[t.Callable, t.Mapping[str, t.Any]]] = None, 
    default: t.Any = None, 
    **kwargs,
)-> t.Any:
    kwargs['first'] = False
    kwargs['last'] = True
    return Data_where(data, callback, default, **kwargs)

def Data_first_filled(*args: t.Any, default: t.Any = None)-> t.Any:
    for data in args:
        if Validate_filled(data):
            return data
    
    return default

def Data_only_with(
    data: t.Iterable[t.Any],
    *args: str,
    **kwargs,
)-> dict[str, t.Any]|list[dict[str, t.Any]]:
    is_meta = kwargs.pop('meta', False)
    is_meta_fix = kwargs.pop('meta_fix', False)
    is_no_dot = kwargs.pop('no_dot', False)
    is_filled = kwargs.pop('filled', False)

    ph = Factory_placeholder(mod='hashed')
    default_missing = kwargs.pop('default_missing', ph)
    default_blank = kwargs.pop('default_blank', ph)

    is_mapping = Validate_is_mapping(data)
    data = Convert_to_pydash(data)
    
    ret = []
    for item in Convert_to_iterable(data):
        keys = Convert_as_copied(list(args))
        
        meta_keys = [meta_key for meta_key in item.keys() if str(meta_key).startswith('_')] if is_meta else []
        if Validate_filled(meta_keys):
            keys.extend(meta_keys)

        new_item = {}
        for key in keys:
            key_exists = (is_no_dot and key in item) or (not is_no_dot and Data_has(item, key))
            
            new_value = item.get(key) if is_no_dot else Data_get(item, key)
            if not key_exists:
                if default_missing != ph:
                    new_value = default_missing
                else:
                    continue
            
            is_value_filled = not is_filled or ((is_no_dot and Validate_filled(item[key])) or (not is_no_dot and Validate_filled(Data_get(item, key))))
            if not is_value_filled:
                if default_blank != ph:
                    new_value = default_blank
                else:
                    continue
            
            is_key_meta = is_meta and str(key).startswith('_')
            new_key = str(key).lstrip('_') if is_key_meta and is_meta_fix else key
            
            if is_no_dot:
                new_item[new_key] = Convert_as_copied(new_value)
            else:
                Data_set(new_item, new_key, Convert_as_copied(new_value))
        
        ret.append(new_item)
    
    return ret[0] if is_mapping else ret

def Data_all_except(
    data: t.Iterable[t.Any],
    *args: str,
    **kwargs,
)-> dict[str, t.Any]|list[dict[str, t.Any]]:
    is_meta = kwargs.pop('meta', False)
    is_omitted = kwargs.pop('omitted', False)
    is_no_dot = kwargs.pop('no_dot', False)
    is_blank = kwargs.pop('blank', False)

    is_mapping = Validate_is_mapping(data)
    data = Convert_to_pydash(data)
    ret = []

    for item in Convert_to_iterable(data):
        keys = list(args)
        
        exclude_keys = [exc_key for exc_key in item.keys() if str(exc_key).startswith('_')] if is_meta else []
        if Validate_filled(exclude_keys):
            keys.extend(exclude_keys)
        
        if is_omitted or is_blank:
            exclude_value_keys = [exc_key for exc_key, exc_value in item.items() if (is_omitted and Validate_is_ansible_omitted(exc_value)) or (is_blank and Validate_blank(exc_value))]
        else:
            exclude_value_keys = []
        
        if Validate_filled(exclude_value_keys):
            keys.extend(exclude_value_keys)

        new_item = Convert_as_copied(item)
        
        for key in keys:
            key_exists = (is_no_dot and key in item) or (not is_no_dot and Data_has(item, key))
            if not key_exists:
                continue
            
            if is_no_dot:
                del new_item[key]
            else:
                Data_unset(new_item, key)
        
        ret.append(new_item)
    
    return ret[0] if is_mapping else ret

def Data_flatten(data, levels=None, skip_nulls=True):
    ret = []
    for element in data:
        if skip_nulls and element in (None, 'None', 'null'):
            continue
        elif Validate_is_sequence(element):
            if levels is None:
                ret.extend(Data_flatten(element, skip_nulls=skip_nulls))
            elif levels >= 1:
                ret.extend(Data_flatten(element, levels=(int(levels) - 1), skip_nulls=skip_nulls))
            else:
                ret.append(element)
        else:
            ret.append(element)

    return ret

def Data_merge_hash(x, y, recursive=True, list_merge='replace'):
    Validate_require_mutable_mappings(x, y)
    
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
                x[key] = Data_merge_hash(x_value, y_value, recursive, list_merge)
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

def Data_combine(*args, **kwargs):
    recursive = kwargs.pop('recursive', False)
    list_merge = kwargs.pop('list_merge', 'replace')
    reverse = kwargs.pop('reverse', False)

    args = list(args)
    if reverse:
        args.reverse()

    dicts = Data_flatten(args, levels=1)

    if Validate_blank(dicts):
        return {}

    if len(dicts) == 1:
        return dicts[0]

    dicts = reversed(dicts)
    result = next(dicts)
    for dictionary in dicts:
        result = Data_merge_hash(dictionary, result, recursive, list_merge)

    return result

def Data_combine_match(
    data: str,
    items: t.Mapping[str, t.Any] | ENUMERATABLE[t.Mapping[str, t.Any]], 
    attribute: str,
    *args, 
    **kwargs
):
    import re
    is_prepare = kwargs.pop('prepare', False)
    ret = []

    for item in Convert_to_iterable(items):
        pattern = Data_get(item, attribute)
        if not Validate_is_string(pattern) or Validate_blank(pattern):
            continue
            
        if is_prepare:
            pattern = Str_wrap(pattern, '^', '$')
            
        if re.match(rf"{pattern}", data):
            ret.append(item)
    
    if Validate_filled(args):
        ret.extend(list(args))
    
    ret = [Convert_to_safe_json(item) if Validate_is_ansible_mapping(item) else item for item in ret]

    return Data_combine(*ret, **kwargs)

def Data_map(
    data: ENUMERATABLE[t.Any], 
    callback: t.Callable, 
)-> list:
    return [Utils_call(callback, val_, key_) for key_, val_ in enumerate(data)]

def Data_keys(
    data: t.Iterable[t.Any],
    **kwargs
)-> t.Any:
    ret = []
    is_mapping = Validate_is_mapping(data)
    replace = kwargs.pop('replace', {})
    
    no_dot = kwargs.pop('no_dot', False)
    ph = Factory_placeholder(mod='hashed')

    for item in Convert_to_iterable(data):
        item_new = Convert_as_copied(item)
    
        for replacement in replace.get('keys', []):
            if not Validate_is_sequence(replacement) or len(replacement) < 2:
                raise ValueError('Key replacement requires at least 2 elements')
        
            key_from = replacement[0]
            key_to = replacement[1]
            if key_from == key_to:
                continue

            key_default = ph
            key_exists = (no_dot and key_from in item_new) or (not no_dot and Data_has(item_new, key_from))

            if len(replacement) > 2:
                key_default = replacement[2]

            value_new = key_default
            if key_exists and no_dot:
                value_new = item_new[key_from]
            elif key_exists and not no_dot:
                value_new = Data_get(item_new, key_from)
            
            if value_new == ph:
                continue

            if no_dot:
                item_new[key_to] = value_new
            else:
                Data_set(item_new, key_to, value_new)

            if key_exists and not Validate_is_falsy(replace.get('remove_replaced', True)):
                if no_dot:
                    del item_new[key_from]
                else:
                    Data_unset(item_new, key_from)
            
        ret.append(item_new)

    return ret[0] if is_mapping else ret