from __future__ import annotations
import re
from collections.abc import Mapping, MutableMapping, Sequence, MutableSequence
from ansible_collections.aybarsm.utils.plugins.module_utils.tools.helper import Helper
from ansible_collections.aybarsm.utils.plugins.module_utils.tools.data import Data
from ansible_collections.aybarsm.utils.plugins.module_utils.tools.validate import Validate
from ansible_collections.aybarsm.utils.plugins.module_utils.tools.str import Str

class Data:
    @staticmethod
    def dot(data, prepend='') -> dict:
        ret = {}
        if Validate.is_sequence(data):
            for key, value in enumerate(data):
                new_key = f"{prepend}{str(key)}"
                if value and (Validate.is_mapping(value) or Validate.is_sequence(value)):
                    ret.update(Data.dot(value, new_key + '.'))
                else:
                    ret[new_key] = value
        elif Validate.is_mapping(data):
            for key, value in data.items():
                new_key = f"{prepend}{key}"
                if value and (Validate.is_mapping(value) or Validate.is_sequence(value)):
                    ret.update(Data.dot(value, new_key + '.'))
                else:
                    ret[new_key] = value
        
        return ret

    @staticmethod
    def undot(data: Mapping) -> dict:
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
                Data.set(ret, key, Data.undot(value))
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
                Data.set(ret, primary, seq.copy())
            else:
                Data.set(ret, key, value)
            
            done.extend(done_iter)
        
        return ret
    
    @staticmethod
    def pydash():
        import pydash
        return pydash

    @staticmethod
    def collection():
        return Data.collections()
    
    @staticmethod
    def collections():
        return Data.pydash().collections
    
    @staticmethod
    def get(data, key, default = None):
        return Data.pydash().get(data, key, default)
    
    @staticmethod
    def set(data, key, value):
        return Data.pydash().set_(data, key, value)
    
    @staticmethod
    def has(data, key):
        return Data.pydash().has(data, key)

    @staticmethod
    def forget(data, key):
        return Data.pydash().unset(data, key)

    @staticmethod
    def pluck(data, key):
        return Data.pydash().pluck(data, key)
    
    @staticmethod
    def invert(data):
        return Data.pydash().invert(data)
    
    @staticmethod
    def flip(data):
        return Data.invert(data)
    
    @staticmethod
    def dot_sort_keys(data: Mapping | Sequence, **kwargs) -> dict | list:
        if not Validate.is_sequence(data) and not Validate.is_mapping(data):
            raise ValueError('Invalid data type to sort')
        
        asc = kwargs.pop('asc', True)
        if Validate.is_mapping(data):
            ret = sorted(dict(data).items(), key=lambda item: item[0].count('.'))
        else:
            ret = sorted([item for item in data], key=lambda s: s.count('.'))

        if not asc:
            ret = reversed(ret)
            
        return dict(ret) if Validate.is_mapping(data) else list(ret)

    @staticmethod
    def iterate(data, callback, *args, **kwargs) -> dict | list[dict]:
        Validate.require(['dict', 'iterable_of_dicts'], data, 'data')
        Validate.require(['callable'], callback, 'callback')
        if Validate.blank(data):
            return data
        
        mode = Data.get(kwargs, 'mode', 'filter')
        if mode not in ['filter', 'map']:
            raise ValueError("Data._iterate: Accepted modes are filter, map")
        
        is_map = mode == 'map'
        is_negate = Data.get(kwargs, 'negate', False)
        if is_map and is_negate:
            raise ValueError("Data._iterate: Negate available only for filter mode")
        
        is_dict = Validate.is_dict(data)
        is_keys = Data.get(kwargs, 'keys', False)
        if not is_dict and is_keys:
            raise ValueError("Data._iterate: Keys available only for dicts")
        
        if is_dict and not is_keys:
            return Helper.callback(callback, data)

        ret = {} if is_dict else (data if is_map else [])

        if is_dict:
            for key, value in data.items():
                res = Helper.callback(callback, value, key)
                if is_map:
                    ret[key] = res
                else:
                    res = not res if is_negate else res
                    if res:
                        ret[key] = value
        else:
            for idx in (range(0, len(data))):
                res = Helper.callback(callback, data[idx], idx)
                if is_map:
                    ret[idx] = res
                else:
                    res = not res if is_negate else res
                    if res:
                        ret.append(data[idx]) #type: ignore
        
        return ret

    @staticmethod
    def only_with(data: dict | Sequence[dict], *args, **kwargs) -> Sequence[dict] | list[dict] | dict:
        Validate.require(['dict', 'iterable_of_dicts'], data, 'data')
        Validate.require(['iterable_of_strings'], args, 'args')

        meta = Data.get(kwargs, 'meta', False)
        meta_fix = Data.get(kwargs, 'meta_fix', False)
        no_dot = Data.get(kwargs, 'no_dot', False)
        filled = Data.get(kwargs, 'filled', False)
        if Validate.blank(args) and not meta:
            return data
        
        ret = []
        is_dict = Validate.is_dict(data)
        args = list(args)

        for item in Helper.to_iterable(data):
            keys = args.copy()
            meta_keys = [meta_key for meta_key in item.keys() if str(meta_key).startswith('_')] if meta else []
            if Validate.filled(meta_keys):
                keys.extend(meta_keys)
            
            new_item = {}
            for key in keys:
                key_exists = (no_dot and key in item) or (not no_dot and Data.has(item, key))
                if not key_exists:
                    continue
                
                is_filled = not filled or ((no_dot and Validate.filled(item[key])) or (not no_dot and Validate.filled(Data.get(item, key))))
                if not is_filled:
                    continue

                is_meta = meta and str(key).startswith('_')
                new_key = str(key).lstrip('_') if is_meta and meta_fix else key
                
                if no_dot:
                    new_item[new_key] = item[key]
                else:
                    Data.set(new_item, new_key, Data.get(item, key))
            
            ret.append(new_item)
        
        return ret[0] if is_dict else ret
    
    @staticmethod
    def all_except(data: dict | Sequence[dict], *args, **kwargs) -> Sequence[dict] | list[dict] | dict:
        Validate.require(['dict', 'iterable_of_dicts'], data, 'data')
        Validate.require(['iterable_of_strings'], args, 'args')

        meta = Data.get(kwargs, 'meta', False)
        omitted = Data.get(kwargs, 'omitted', False)
        blank = Data.get(kwargs, 'blank', False)
        no_dot = Data.get(kwargs, 'no_dot', False)
        if Validate.blank(args) and not meta and not omitted and not blank:
            return data

        is_dict = Validate.is_dict(data)
        args = list(args)
        ret = []

        for item in Helper.to_iterable(data):
            keys = args.copy()
            
            exclude_keys = [exc_key for exc_key in item.keys() if str(exc_key).startswith('_')] if meta else []
            if Validate.filled(exclude_keys):
                keys.extend(exclude_keys)
            
            exclude_value_keys = [exc_key for exc_key, exc_value in item.items() if (omitted and Validate.is_omitted(exc_value)) or (blank and Validate.blank(exc_value))] if omitted or blank else []
            if Validate.filled(exclude_value_keys):
                keys.extend(exclude_value_keys)

            new_item = item.copy()
            
            for key in keys:
                key_exists = (no_dot and key in item) or (not no_dot and Data.has(item, key))
                if not key_exists:
                    continue
                
                if no_dot:
                    del new_item[key]
                else:
                    Data.forget(new_item, key)
            
            ret.append(new_item)
        
        return ret[0] if is_dict else ret

    @staticmethod
    def query(data, query, *args, **kwargs):
        from ansible_collections.aybarsm.utils.plugins.module_utils.tools.data_query import DataQuery
        dq = DataQuery(query, data, *args, **kwargs)

        return dq.results()
    
    @staticmethod
    def flatten(data, levels=None, skip_nulls=True):
        ret = []
        for element in data:
            if skip_nulls and element in (None, 'None', 'null'):
                continue
            elif Validate.is_sequence(element):
                if levels is None:
                    ret.extend(Data.flatten(element, skip_nulls=skip_nulls))
                elif levels >= 1:
                    ret.extend(Data.flatten(element, levels=(int(levels) - 1), skip_nulls=skip_nulls))
                else:
                    ret.append(element)
            else:
                ret.append(element)

        return ret
    
    @staticmethod
    def merge_hash(x, y, recursive=True, list_merge='replace'):
        Validate.mutable_mappings(x, y)
        
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

            if isinstance(x_value, MutableMapping) and isinstance(y_value, MutableMapping):
                if recursive:
                    x[key] = Data.merge_hash(x_value, y_value, recursive, list_merge)
                else:
                    x[key] = y_value
                continue

            if isinstance(x_value, MutableSequence) and isinstance(y_value, MutableSequence):
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
    
    @staticmethod
    def combine(*args, **kwargs):
        recursive = kwargs.pop('recursive', False)
        list_merge = kwargs.pop('list_merge', 'replace')
        reverse = kwargs.pop('reverse', False)

        args = list(args)
        if reverse:
            args.reverse()

        dicts = Data.flatten(args, levels=1)

        if Validate.blank(dicts):
            return {}

        if len(dicts) == 1:
            return dicts[0]

        dicts = reversed(dicts)
        result = next(dicts)
        for dictionary in dicts:
            result = Data.merge_hash(dictionary, result, recursive, list_merge)

        return result
    
    @staticmethod
    def combine_match(data, items, attribute, *args, **kwargs):
        Validate.require('string', data, 'data')
        Validate.require('string', attribute, 'attribute')
        Validate.require(['dict', 'iterable_of_dicts'], items, 'items')        

        is_prepare = kwargs.pop('prepare', False)
        ret = []

        for item in Helper.to_iterable(items):
            pattern = Data.get(item, attribute)
            if not Validate.is_string(pattern) or Validate.blank(pattern):
                continue
                
            if is_prepare:
                pattern = Str.wrap(pattern, '^', '$')
                
            if re.match(rf"{pattern}", data):
                ret.append(item)
        
        if Validate.filled(args):
            ret.extend(list(args))
        
        ret = [Helper.to_safe_json(item) if Validate.is_ansible_mapping(item) else item for item in ret]

        return Data.combine(*ret, **kwargs)

    @staticmethod
    def difference(a: Sequence, b: Sequence, *args: Sequence) -> list:
        if not Validate.is_sequence(a) or not Validate.is_sequence(b):
            raise ValueError('Invalid sequence type')
        
        ret = set(a) - set(b)

        for seq in args:
            if not Validate.is_sequence(seq):
                raise ValueError('Invalid sequence type')
            
            ret = set(ret) - set(seq)
        
        return list(ret)
    
    @staticmethod
    def append(data, key: str, value, **kwargs) -> None:
        is_ioi_extend = kwargs.pop('ioi_extend', False)
        exclude = kwargs.pop('exclude', [])
        is_unique = kwargs.pop('unique', False)

        current = list(Data.get(data, key, []))
        if is_ioi_extend and Validate.is_iterable_of_iterables(value):
            current.extend(value)
        else:
            current.append(value)
        
        if Validate.filled(exclude):
            for exc in exclude:
                exc = Helper.to_iterable(exc)
                current = Data.difference(current, exc)
        
        if is_unique:
            current = list(set(current))

        Data.set(data, key, current.copy())