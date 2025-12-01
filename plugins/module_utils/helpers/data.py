import typing as t
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.types import (
    ENUMERATABLE
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    _convert, _factory, _str, _utils, _validate, _pydash
)

Convert = _convert()
Factory = _factory()
Str = _str()
Utils = _utils()
Validate = _validate()

def pydash():
    return _pydash()

def collections():
    return _pydash().collections

def get(data: t.Iterable[t.Any], key: int|str, default: t.Any = None)-> t.Any:
    if not str(key) == '*' and not Validate.str_contains(str(key), '.*', '*.'):
        return pydash().get(data, key, default)
    
    skip_ = []
    ret = Convert.as_copied(data)
    segments = str(key).strip('.').split('.')
    for idx_, segment in enumerate(segments):
        if idx_ in skip_:
            continue
        
        if segment == '*' and len(segments) > 1 and idx_ < len(segments) - 1 and segments[idx_ + 1] != '*' and Validate.is_iterable_of_not_mappings(ret):
            _flatten = flatten(ret, levels=1)
            if Validate.is_iterable_of_mappings(_flatten):
                ret = _flatten

            ret = pluck(ret, segments[idx_ + 1])
            skip_.append(idx_ + 1)
        elif segment == '*' and Validate.is_mapping(ret):
            ret = list(dict(ret).values())
        elif segment != '*' and Validate.is_iterable_of_mappings(ret):
            ret = pluck(ret, segment)
        elif segment != '*' and Validate.is_mapping(ret):
            ret = Convert.as_copied(pydash().get(ret, segment))       
        elif segment == '*':
            ret = flatten(ret, levels=1)
        
        if idx_ <= len(segments) - 1 and not Validate.is_iterable(ret):
            ret = default
            break

    return ret

def set_(data: t.Iterable[t.Any], key: str, value: t.Any)-> t.Any:
    return pydash().set_(data, key, value) #type: ignore

def has(data: t.Any, key)-> bool:
    return pydash().has(data, key)

def forget(data: t.Iterable[t.Any], *args: str)-> t.Any:
    for key_ in args:
        pydash().unset(data, key_) #type: ignore
    
    return data #type: ignore

def pluck(data, key: int|str, **kwargs) -> list[t.Any]:
    is_unique = kwargs.pop('unique', False)
    is_filled = kwargs.pop('filled', False)

    ret = pydash().pluck(data, key)
    if is_unique == True:
        ret = unique(ret)
    
    if is_filled == True:
        ret = [item for item in ret if Validate.filled(item)]

    return ret

def unique(data: ENUMERATABLE[t.Any]) -> list[t.Any]:
    ret = list(set([item for item in data if Validate.is_hashable(item)]))
    seen = set()
    
    for item in [item for item in data if not Validate.is_hashable(item)]:
        if str(id(item)) not in seen:
            ret.append(item)
            seen.add(str(id(item)))
    
    return ret

def invert(data):
    return pydash().invert(data)

def flip(data):
    return invert(data)

def walk(data: t.Iterable[t.Any], callback = t.Callable):
    return collections().map_(data, callback)

def walk_values_deep(data: t.Iterable[t.Any], callback = t.Callable):
    return pydash().map_values_deep(data, callback)

def _sequence_a_b(a: t.Sequence[t.Any], b: t.Sequence[t.Any], callback: t.Callable, *args: t.Sequence[t.Any])-> list:
    if not Validate.is_sequence(a) or not Validate.is_sequence(b):
        raise ValueError('Invalid sequence type')
    
    ret = Utils.call(callback, a, b)
    for seq in args:
        if not Validate.is_sequence(seq):
            raise ValueError('Invalid sequence type')
        
        ret = Utils.call(callback, ret, seq)
    
    return list(ret)

def difference(a: t.Sequence[t.Any], b: t.Sequence[t.Any], *args: t.Sequence[t.Any])-> list:
    return _sequence_a_b(a, b, lambda seq_a, seq_b: set(seq_a) - set(seq_b), *args) #type: ignore

def intersect(a: t.Sequence, b: t.Sequence, *args: t.Sequence)-> list:
    return _sequence_a_b(a, b, lambda seq_a, seq_b: set(seq_a) & set(seq_b), *args) #type: ignore

def _append_or_prepend(data: t.Iterable[t.Any], key: str, value: t.Any, is_prepend: bool, **kwargs) -> t.Iterable[t.Any]:
    is_extend = kwargs.pop('extend', False)
    is_unique = kwargs.pop('unique', False)
    is_sorted = kwargs.pop('sort', False)
    
    if Validate.is_mapping(data) or Validate.filled(key):
        current = Convert.as_copied(list(get(data, key, [])))
    else:
        current = Convert.as_copied(list(data))
    
    for item in Convert.to_iterable(value):
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
        
    if Validate.is_mapping(data) or Validate.filled(key):
        set_(data, key, current)
    else:
        data = current
    
    return data

def append(data: t.Iterable[t.Any], key: str, value: t.Any, **kwargs) -> t.Iterable[t.Any]:
    return _append_or_prepend(data, key, value, False, **kwargs)

def prepend(data: t.Iterable[t.Any], key: str, value: t.Any, **kwargs) -> t.Iterable[t.Any]:
    return _append_or_prepend(data, key, value, True, **kwargs)

def dot(data: t.Union[t.Sequence[t.Any], t.Mapping[t.Any, t.Any]], prepend='', **kwargs)-> dict:
    is_main = Validate.blank(prepend)
    is_main_mapping = is_main and Validate.is_mapping(data)
    if is_main_mapping:
        data = undot(data) #type: ignore

    ret = {}
    if Validate.is_sequence(data):
        for key, value in enumerate(data):
            new_key = f"{prepend}{str(key)}"
            if value and (Validate.is_mapping(value) or Validate.is_sequence(value)):
                ret.update(dot(value, new_key + '.'))
            else:
                ret[new_key] = value
    elif Validate.is_mapping(data):
        for key, value in data.items(): #type: ignore
            new_key = f"{prepend}{key}"
            if value and (Validate.is_mapping(value) or Validate.is_sequence(value)):
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
    if Validate.blank(data):
        return data
    
    done = []
    ret = {}
    for key, value in data.items():
        if key in done:
            continue
        
        done_iter = [key]
        if Validate.is_mapping(value):
            set_(ret, key, undot(value))
        elif '.' not in str(key):
            ret[key] = value
        elif Validate.str_is_int(Str.after_last(key, '.')):
            primary = Str.before_last(key, '.')
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
    if Validate.is_mapping(data):
        ret = sorted(dict(data).items(), key=lambda item: item[0].count(char)) #type: ignore
    else:
        ret = sorted([item for item in list(data)], key=lambda s: s.count(char))

    if not asc:
        ret = reversed(ret)
    
    if raw:
        return ret #type: ignore
    
    if Validate.is_mapping(data):
        return dict(ret) #type: ignore
    else:
        return list(ret)

def dot_sort_keys(
    data: t.Iterable[t.Any],
    **kwargs
)-> dict|list:
    return sort_keys_char_count(data, '.', **kwargs)

def filled(data: t.Iterable[t.Any], key: str, **kwargs)-> bool:
    return Validate.filled(get(data, key, **kwargs))

def blank(data: t.Iterable[t.Any], key: str, **kwargs)-> bool:
    return Validate.blank(get(data, key, **kwargs))

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

    if Validate.blank(data):
        return default
    
    is_mapping = Validate.is_mapping(data)
    data = Convert.to_iterable(data)    
    
    if Validate.is_mapping(callback):
        callback = Convert.from_mapping_to_callable(dict(callback), **kwargs) #type: ignore
    
    if is_first and not callback:
        if not is_mapping:
            return data[0]
        else:
           return data[list(data[0].keys())[0]]
    
    ret = []

    for key_, val_ in data[0].items() if is_mapping else enumerate(data):
        res = Utils.call(callback, val_, key_) #type: ignore
        if is_negate:
            res = not res
        
        if res != True:
            continue
        
        if is_key:
            ret.append(key_)
        elif not is_mapping:
            ret.append(val_)
        else:
            if Validate.blank(ret):
                ret.append({})
            
            ret[0][key_] = val_
        
        if is_first:
            break

    if Validate.blank(ret):
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
        if Validate.filled(data):
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

    ph = Factory.placeholder(mod='hashed')
    default_missing = kwargs.pop('default_missing', ph)
    default_blank = kwargs.pop('default_blank', ph)

    is_mapping = Validate.is_mapping(data)
    data = Convert.to_pydash(data)
    
    ret = []
    for item in Convert.to_iterable(data):
        keys = Convert.as_copied(list(args))
        
        meta_keys = [meta_key for meta_key in item.keys() if str(meta_key).startswith('_')] if is_meta else []
        if Validate.filled(meta_keys):
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
            
            is_value_filled = not is_filled or ((is_no_dot and Validate.filled(item[key])) or (not is_no_dot and Validate.filled(get(item, key))))
            if not is_value_filled:
                if default_blank != ph:
                    new_value = default_blank
                else:
                    continue
            
            is_key_meta = is_meta and str(key).startswith('_')
            new_key = str(key).lstrip('_') if is_key_meta and is_meta_fix else key
            
            if is_no_dot:
                new_item[new_key] = Convert.as_copied(new_value)
            else:
                set_(new_item, new_key, Convert.as_copied(new_value))
        
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

    is_mapping = Validate.is_mapping(data)
    data = Convert.to_pydash(data)
    ret = []

    for item in Convert.to_iterable(data):
        keys = list(args)
        
        exclude_keys = [exc_key for exc_key in item.keys() if str(exc_key).startswith('_')] if is_meta else []
        if Validate.filled(exclude_keys):
            keys.extend(exclude_keys)
        
        if is_omitted or is_blank:
            exclude_value_keys = [exc_key for exc_key, exc_value in item.items() if (is_omitted and Validate.is_ansible_omitted(exc_value)) or (is_blank and Validate.blank(exc_value))]
        else:
            exclude_value_keys = []
        
        if Validate.filled(exclude_value_keys):
            keys.extend(exclude_value_keys)

        new_item = Convert.as_copied(item)
        
        for key in keys:
            key_exists = (is_no_dot and key in item) or (not is_no_dot and has(item, key))
            if not key_exists:
                continue
            
            if is_no_dot:
                del new_item[key]
            else:
                forget(new_item, key)
        
        ret.append(new_item)
    
    return ret[0] if is_mapping else ret

def flatten(data, levels=None, skip_nulls=True):
    ret = []
    for element in data:
        if skip_nulls and element in (None, 'None', 'null'):
            continue
        elif Validate.is_sequence(element):
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
    Validate.require_mutable_mappings(x, y)
    
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

    if Validate.blank(dicts):
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

    for item in Convert.to_iterable(items):
        pattern = get(item, attribute)
        if not Validate.is_string(pattern) or Validate.blank(pattern):
            continue
            
        if is_prepare:
            pattern = Str.wrap(pattern, '^', '$')
            
        if re.match(rf"{pattern}", data):
            ret.append(item)
    
    if Validate.filled(args):
        ret.extend(list(args))
    
    ret = [Convert.to_safe_json(item) if Validate.is_ansible_mapping(item) else item for item in ret]

    return combine(*ret, **kwargs)

def map(
    data: ENUMERATABLE[t.Any], 
    callback: t.Callable, 
)-> list:
    return [Utils.call(callback, val_, key_) for key_, val_ in enumerate(data)]

def unique_by(
    data: ENUMERATABLE[t.Mapping[str, t.Any]],
    by: ENUMERATABLE[str] | t.Callable,
    **kwargs
)-> list[dict]:
    unique_hashes = []
    ret = []
    ph = Factory.placeholder(mod='hashed')
    
    for idx, item in enumerate(data):
        if Validate.is_callable(by):
            unique_hash = Utils.call(by, item, idx) #type: ignore
        else:
            unique_parts = only_with(item, *by, default_missing=ph, default_blank=ph).values() #type: ignore
            unique_hash = Convert.to_md5('|'.join([Convert.to_text(unique_value) for unique_value in unique_parts]))

        if unique_hash not in unique_hashes:
            ret.append(item)
            unique_hashes.append(unique_hash)
    
    return ret

def keys(
    data: t.Iterable[t.Any],
    **kwargs
)-> t.Any:
    ret = []
    is_mapping = Validate.is_mapping(data)
    replace = kwargs.pop('replace', {})
    
    no_dot = kwargs.pop('no_dot', False)
    ph = Factory.placeholder(mod='hashed')

    for item in Convert.to_iterable(data):
        item_new = Convert.as_copied(item)
    
        for replacement in replace.get('keys', []):
            if not Validate.is_sequence(replacement) or len(replacement) < 2:
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

            if key_exists and not Validate.is_falsy(replace.get('remove_replaced', True)):
                if no_dot:
                    del item_new[key_from]
                else:
                    forget(item_new, key_from)
            
        ret.append(item_new)

    return ret[0] if is_mapping else ret

# def walk_recursive(
#     data: t.Mapping[t.Any, t.Any]|t.Sequence[t.Any],
#     callback = t.Callable
# )-> dict|list:
#     if Validate.is_mapping(data):
#         ret = {}
#         for key_, value_ in dict(data).items():
#             if Validate.is_mapping(data) or Validate.is_sequence(value_):
#                 ret[key_] = walk_recursive(value_, callback)
#             else:
#                 ret[key_] = Utils.call(callback, value_, key_)
#     elif Validate.is_sequence(data):
#         ret = []
#         for idx_, value_ in enumerate(list(data)):
#             if Validate.is_mapping(data) or Validate.is_sequence(value_):
#                 ret.append(walk_recursive(value_, callback))
#             else:
#                 ret.append(Utils.call(callback, value_, idx_))

#     return ret

# def dot_sort_keys(
#         data: t.Union[t.Sequence[str], t.Mapping[str, t.Any]],
#         **kwargs
#     )-> dict|list:
    
#     asc = kwargs.pop('asc', True)
#     asc_keys = kwargs.pop('asc_keys', True)
#     raw = kwargs.pop('raw', False)

#     if Validate.is_mapping(data):
#         data = dot(undot(data)) #type: ignore
#         keys = data.keys()
#     else:
#         keys = data
    
#     counted = {}
#     for key_ in keys:
#         key_ = str(key_)
#         count_key = str(key_.count('.'))
#         if count_key not in counted:
#             counted[count_key] = [key_]
#         else:
#             counted[count_key].append(key_)
    
#     return sorted(counted.items()) if asc else reversed(sorted(counted.items()))
    # for count_, key_ in sorted(counted.items()) if asc else reversed(sorted(counted.items())):



    # ret = {}
    # for key_, value_ in iterate:
    #     count_key = str(str(key_ if is_mapping else value_).count('.'))
        
    #     if count_key not in ret:
    #         ret[count_key] = {} if is_mapping else []
        

        
        
    # if Validate.is_mapping(data):
        
    # else:

    # if Validate.is_mapping(data):
    #     ret = sorted(dict(data).items(), key=lambda item: item[0].count('.'))
    # else:
    #     ret = sorted([item for item in list(data)], key=lambda s: s.count('.'))

    # if not asc:
    #     ret = reversed(ret)
    
    # if raw:
    #     return ret # type: ignore
    
    # if Validate.is_mapping(data):
    #     return dict(ret)
    # else:
    #     return list(ret)