import typing as T
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    __convert, __factory, __str, __utils, __validate, __pydash
)

def collections():
    return __pydash().collections

def get(data: T.Union[T.Sequence[T.Any], T.Mapping[T.Any, T.Any]], key: str, default: T.Any = None)-> T.Any:
    return __pydash().get(data, key, default)

def set_(data: T.Union[T.Sequence[T.Any], T.Mapping[T.Any, T.Any]], key: str, value: T.Any)-> T.Any:
    return __pydash().set_(data, key, value) #type: ignore

def has(data: T.Any, key)-> bool:
    return __pydash().has(data, key)

def forget(data: T.Union[T.Sequence[T.Any], T.Mapping[T.Any, T.Any]], *args: str)-> T.Any:
    for key_ in args:
        __pydash().unset(data, key_) #type: ignore
    
    return data #type: ignore

def pluck(data, key):
    return __pydash().pluck(data, key)

def invert(data):
    return __pydash().invert(data)

def flip(data):
    return invert(data)

def difference(a: T.Sequence[T.Any], b: T.Sequence[T.Any], *args: T.Sequence[T.Any]) -> list:
    if not __validate().is_sequence(a) or not __validate().is_sequence(b):
        raise ValueError('Invalid sequence type')
    
    ret = set(a) - set(b)

    for seq in args:
        if not __validate().is_sequence(seq):
            raise ValueError('Invalid sequence type')
        
        ret = set(ret) - set(seq)
    
    return list(ret)

def append(
    data: T.Union[T.Sequence[T.Any], T.Mapping[T.Any, T.Any]],
    key: str,
    value: T.Any,
    **kwargs
)-> T.Any:
    current = list(get(data, key, []))
    is_extend = kwargs.pop('extend', False)
    is_unique = kwargs.pop('unique', False)
    is_sorted = kwargs.pop('sort', False)

    if is_extend:
        current.extend(value)
    else:
        current.append(value)

    if is_unique:
        current = list(set(current))
    
    if is_sorted:
        current = list(sorted(current))
    
    return set_(data, key, current.copy())

def prepend(
    data: T.Union[T.Sequence[T.Any], T.Mapping[T.Any, T.Any]],
    key: str,
    value: T.Any,
    **kwargs
)-> T.Any:
    current = list(get(data, key, []))
    is_extend = kwargs.pop('extend', False)
    is_unique = kwargs.pop('unique', False)
    is_sorted = kwargs.pop('sort', False)

    if is_extend:
        for item in __convert().to_iterable(value):
            current.insert(0, item)
    else:
        current.insert(0, value)

    if is_unique:
        current = list(set(current))
    
    if is_sorted:
        current = list(sorted(current))
    
    return set_(data, key, current.copy())

def dot(data: T.Union[T.Sequence[T.Any], T.Mapping[T.Any, T.Any]], prepend='', **kwargs)-> dict:
    is_main = __validate().blank(prepend)
    is_main_mapping = is_main and __validate().is_mapping(data)
    if is_main_mapping:
        data = undot(data) #type: ignore

    ret = {}
    if __validate().is_sequence(data):
        for key, value in enumerate(data):
            new_key = f"{prepend}{str(key)}"
            if value and (__validate().is_mapping(value) or __validate().is_sequence(value)):
                ret.update(dot(value, new_key + '.'))
            else:
                ret[new_key] = value
    elif __validate().is_mapping(data):
        for key, value in data.items(): #type: ignore
            new_key = f"{prepend}{key}"
            if value and (__validate().is_mapping(value) or __validate().is_sequence(value)):
                ret.update(dot(value, new_key + '.'))
            else:
                ret[new_key] = value
    
    if is_main_mapping:
        sorted = kwargs.pop('sorted', False)
        if sorted:
            asc = kwargs.pop('asc', True)
            ret = dict(sorted(ret.items()) if asc else reversed(sorted(ret.items())))
    
    return ret

def undot(data: T.Mapping)-> dict:
    import re
    data = dict(data)
    if __validate().blank(data):
        return data
    
    done = []
    ret = {}
    for key, value in data.items():
        if key in done:
            continue
        
        done_iter = [key]
        if __validate().is_mapping(value):
            set_(ret, key, undot(value))
        elif '.' not in str(key):
            ret[key] = value
        elif __validate().is_str_int(__str().after_last(key, '.')):
            primary = __str().before_last(key, '.')
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

def dot_sort_keys(
    data: T.Union[T.Sequence[str], T.Mapping[str, T.Any]],
    **kwargs
)-> dict|list:
    
    asc = kwargs.pop('asc', True)
    raw = kwargs.pop('raw', False)
    if __validate().is_mapping(data):
        ret = sorted(dict(data).items(), key=lambda item: item[0].count('.')) #type: ignore
    else:
        ret = sorted([item for item in list(data)], key=lambda s: s.count('.'))

    if not asc:
        ret = reversed(ret)
    
    if raw:
        return ret #type: ignore
    
    if __validate().is_mapping(data):
        return dict(ret) #type: ignore
    else:
        return list(ret)

def filled(data: T.Union[T.Sequence[T.Any], T.Mapping[T.Any, T.Any]], key: str, **kwargs)-> bool:
    return __validate().filled(get(data, key, **kwargs))

def blank(data: T.Union[T.Sequence[T.Any], T.Mapping[T.Any, T.Any]], key: str, **kwargs)-> bool:
    return __validate().blank(get(data, key, **kwargs))

def where(
    data: T.Union[T.Sequence[T.Any], T.Mapping[T.Any, T.Any]], 
    callback: T.Optional[T.Union[T.Callable, T.Mapping[str, T.Any]]] = None, 
    default: T.Any = None, 
    **kwargs: T.Mapping[str, bool],
)-> T.Any:
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
    
    is_iter = __validate().is_sequence(data)
    data = list(data) if is_iter else dict(data)

    if __validate().blank(data):
        return default
    
    if is_iter and __validate().is_mapping(callback):
        callback = __convert().from_mapping_to_callable(callback, **kwargs) #type: ignore

    if is_first and is_iter and not callback:
        return data[0]
    elif is_first and not is_iter and not callback:
        first_key = list(data.keys())[0] #type: ignore
        return data[first_key]
    else:
        ret = [] if is_iter else {}
        iterate = enumerate(data) if is_iter else data.items() #type: ignore
        for key, value in iterate:
            res = __utils().call(callback, value, key) #type: ignore
            if is_negate:
                res = not res
            
            if res == True:
                if is_iter:
                    if is_key:
                        ret.append(key) #type: ignore
                    else:
                        ret.append(value) #type: ignore
                else:
                    ret[key] = value
                
                if is_first:
                    break

    if __validate().blank(ret):
        return default
    
    if is_first or is_last:
        if not is_iter:
            ret_keys = ret.keys() #type: ignore
            return ret[ret_keys[0]] if is_first else ret[ret_keys[-1]] #type: ignore
        else:
            return ret[0] if is_first else ret[-1]

    return ret

def reject(
    data: T.Union[T.Sequence[T.Any], T.Mapping[T.Any, T.Any]], 
    callback: T.Optional[T.Union[T.Callable, T.Mapping[str, T.Any]]] = None, 
    default: T.Any = None, 
    **kwargs,
)-> T.Any:
    kwargs['negate'] = True
    return where(data, callback, default, **kwargs)

def first(
    data: T.Union[T.Sequence[T.Any], T.Mapping[T.Any, T.Any]], 
    callback: T.Optional[T.Union[T.Callable, T.Mapping[str, T.Any]]] = None, 
    default: T.Any = None, 
    **kwargs,
)-> T.Any:
    kwargs['first'] = True
    kwargs['last'] = False
    return where(data, callback, default, **kwargs)

def last(
    data: T.Union[T.Sequence[T.Any], T.Mapping[T.Any, T.Any]], 
    callback: T.Optional[T.Union[T.Callable, T.Mapping[str, T.Any]]] = None, 
    default: T.Any = None, 
    **kwargs,
)-> T.Any:
    kwargs['first'] = False
    kwargs['last'] = True
    return where(data, callback, default, **kwargs)

def first_filled(*args: T.Any, default: T.Any = None)-> T.Any:
    for data in args:
        if __validate().filled(data):
            return data
    
    return default

def only_with(
    data: T.Union[T.Mapping[str, T.Any], T.Sequence[T.Mapping[str, T.Any]]],
    *args: str,
    **kwargs,
)-> dict[str, T.Any]|list[dict[str, T.Any]]:
    is_meta = kwargs.pop('meta', False)
    is_meta_fix = kwargs.pop('meta_fix', False)
    is_no_dot = kwargs.pop('no_dot', False)
    is_filled = kwargs.pop('filled', False)

    ph = __factory().placeholder(mod='hashed')
    default_missing = kwargs.pop('default_missing', ph)
    default_blank = kwargs.pop('default_blank', ph)

    is_mapping = __validate().is_mapping(data)
    data = __convert().to_pydash(data)
    
    ret = []
    for item in __convert().to_iterable(data):
        keys = __convert().as_copied(list(args))
        
        meta_keys = [meta_key for meta_key in item.keys() if str(meta_key).startswith('_')] if is_meta else []
        if __validate().filled(meta_keys):
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
            
            is_value_filled = not is_filled or ((is_no_dot and __validate().filled(item[key])) or (not is_no_dot and __validate().filled(get(item, key))))
            if not is_value_filled:
                if default_blank != ph:
                    new_value = default_blank
                else:
                    continue
            
            is_key_meta = is_meta and str(key).startswith('_')
            new_key = str(key).lstrip('_') if is_key_meta and is_meta_fix else key
            
            if is_no_dot:
                new_item[new_key] = __convert().as_copied(new_value)
            else:
                set_(new_item, new_key, __convert().as_copied(new_value))
        
        ret.append(new_item)
    
    return ret[0] if is_mapping else ret

def all_except(
    data: T.Union[T.Mapping[str, T.Any], T.Sequence[T.Mapping[str, T.Any]]],
    *args: str,
    **kwargs,
)-> dict[str, T.Any]|list[dict[str, T.Any]]:
    is_meta = kwargs.pop('meta', False)
    is_omitted = kwargs.pop('omitted', False)
    is_no_dot = kwargs.pop('no_dot', False)
    is_blank = kwargs.pop('blank', False)

    is_mapping = __validate().is_mapping(data)
    data = __convert().to_pydash(data)
    ret = []

    for item in __convert().to_iterable(data):
        keys = list(args)
        
        exclude_keys = [exc_key for exc_key in item.keys() if str(exc_key).startswith('_')] if is_meta else []
        if __validate().filled(exclude_keys):
            keys.extend(exclude_keys)
        
        if is_omitted or is_blank:
            exclude_value_keys = [exc_key for exc_key, exc_value in item.items() if (is_omitted and __validate().is_ansible_omitted(exc_value)) or (is_blank and __validate().blank(exc_value))]
        else:
            exclude_value_keys = []
        
        if __validate().filled(exclude_value_keys):
            keys.extend(exclude_value_keys)

        new_item = __convert().as_copied(item)
        
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
        elif __validate().is_sequence(element):
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
    __validate().require_mutable_mappings(x, y)
    
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

        if isinstance(x_value, T.MutableMapping) and isinstance(y_value, T.MutableMapping):
            if recursive:
                x[key] = merge_hash(x_value, y_value, recursive, list_merge)
            else:
                x[key] = y_value
            continue

        if isinstance(x_value, T.MutableSequence) and isinstance(y_value, T.MutableSequence):
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

    if __validate().blank(dicts):
        return {}

    if len(dicts) == 1:
        return dicts[0]

    dicts = reversed(dicts)
    result = next(dicts)
    for dictionary in dicts:
        result = merge_hash(dictionary, result, recursive, list_merge)

    return result

def map(
    data: T.Sequence[T.Any], 
    callback: T.Callable, 
)-> list:
    return [__utils().call(callback, val_, key_) for key_, val_ in enumerate(data)]

# def dot_sort_keys(
#         data: T.Union[T.Sequence[str], T.Mapping[str, T.Any]],
#         **kwargs
#     )-> dict|list:
    
#     asc = kwargs.pop('asc', True)
#     asc_keys = kwargs.pop('asc_keys', True)
#     raw = kwargs.pop('raw', False)

#     if __validate().is_mapping(data):
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
        

        
        
    # if __validate().is_mapping(data):
        
    # else:

    # if __validate().is_mapping(data):
    #     ret = sorted(dict(data).items(), key=lambda item: item[0].count('.'))
    # else:
    #     ret = sorted([item for item in list(data)], key=lambda s: s.count('.'))

    # if not asc:
    #     ret = reversed(ret)
    
    # if raw:
    #     return ret # type: ignore
    
    # if __validate().is_mapping(data):
    #     return dict(ret)
    # else:
    #     return list(ret)