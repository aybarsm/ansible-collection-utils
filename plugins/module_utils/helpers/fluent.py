import typing as T
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    __convert, __data, __validate, __utils, __pydash,
)

Convert = __convert()
Data = __data()
Utils = __utils()
Validate = __validate()

class Fluent(object):
    on_save: T.Optional[T.Callable] = None
    on_destroy: T.Optional[T.Callable] = None

    def __init__(self, data: T.Mapping[T.Any, T.Any] = {}):
        self.data: dict[T.Any, T.Any] = dict(data).copy()
    
    def get(self, key: str, default: T.Any = None)-> T.Any:
        return Data.get(self.data, key, default)
    
    def get_filled(self, key: str, default, **kwargs)-> T.Any:
        if not self.has(key):
            return default
        
        ret = self.get(key)
        return default if not Validate.filled(ret, **kwargs) else ret
    
    def set(self, key: str, value: T.Any)-> dict:
        Data.set_(self.data, key, value)
        return self.data
    
    def increase(self, key: str, start: int|float = 0, step: int|float = 1)-> int | float:
        current = self.get(key, start)
        current += step
        self.set(key, current)
        return current
    
    def decrease(self, key: str, start: int|float = 0, step: int|float = 1)-> int | float:
        current = self.get(key, start)
        current -= step
        self.set(key, current)
        return current
    
    def forget(self, key: str)-> dict:
        Data.forget(self.data, key)
        return self.data
    
    def unset(self, key: str)-> dict:
        return self.forget(key)

    def has(self, key: str)-> bool:
        return Data.has(self.data, key)

    def filled(self, key: str)-> bool:
        return Validate.filled(self.get(key))
    
    def contains(self, key: str, *args, **kwargs)-> bool:
        return Validate.contains(self.get(key, []), *args, **kwargs)

    def blank(self, key: str)-> bool:
        return Validate.blank(self.get(key))
    
    def append(self, key: str, value, **kwargs)-> dict:
        self.data = dict(Data.append(self.data, key, value, **kwargs))
        return self.data

    def prepend(self, key: str, value, **kwargs)-> dict:
        self.data = dict(Data.prepend(self.data, key, value, **kwargs))
        return self.data
    
    def pop(self, key: str, default: T.Any = None) -> T.Any:
        current = list(self.get(key, []))
        
        if Validate.filled(current):
            ret = current.pop()
        else:
            ret = default
        
        self.set(key, current)

        return ret

    def where(self, callback: T.Callable, default: T.Any = None, **kwargs) -> T.Any:
        return Data.where(self.all(), callback, default, **kwargs)
    
    def reject(self, callback: T.Callable, default: T.Any = None, **kwargs) -> T.Any:
        return Data.reject(self.all(), callback, default, **kwargs)

    def first(self, callback: T.Callable, default: T.Any = None, **kwargs) -> T.Any:
        return Data.first(self.all(), callback, default, **kwargs)
    
    def last(self, callback: T.Callable, default: T.Any = None, **kwargs) -> T.Any:
        return Data.last(self.all(), callback, default, **kwargs)
    
    def where_key(self, callback: T.Callable, default: T.Any = None, **kwargs) -> T.Any:
        kwargs['key'] = True
        return self.where(callback, default, **kwargs)
    
    def reject_key(self, callback: T.Callable, default: T.Any = None, **kwargs) -> T.Any:
        kwargs['key'] = True
        return self.reject(callback, default, **kwargs)

    def first_key(self, callback: T.Callable, default: T.Any = None, **kwargs) -> T.Any:
        kwargs['key'] = True
        return self.first(callback, default, **kwargs)
    
    def last_key(self, callback: T.Callable, default: T.Any = None, **kwargs) -> T.Any:
        kwargs['key'] = True
        return self.last(callback, default, **kwargs)

    def keys(self)-> list[str]:
        return [str(key_) for key_ in self.data.keys()]

    def all(self)-> dict:
        return self.data.copy()
    
    def items(self, key_name: str = 'key', value_name: str = 'value',)-> list[dict[str, T.Any]]:
        return Convert.to_items(self.all(), key_name, value_name)

    def only_with(self, *args, **kwargs):
        return Data.only_with(self.all(), *args, **kwargs)
    
    def all_except(self, *args, **kwargs):
        return Data.all_except(self.all(), *args, **kwargs)
    
    def empty(self)-> bool:
        return Validate.blank(self.data)
    
    def not_empty(self)-> bool:
        return not self.empty()
    
    def pydash(self):
        return __pydash()
    
    def copy(self):
        return Fluent(self.all())
    
    def combine(self, data: T.Mapping, key: str, **kwargs)-> None:
        if Validate.blank(key):
            self.data = Data.combine(self.all(), dict(data), **kwargs)
        else:
            self.set(key, Data.combine(self.get(key, {}), dict(data), **kwargs))
    
    def __copy__(self):
        return self.copy()

    def __deepcopy__(self):
        return self.copy()
    
    def save(self)-> None:
        if not self.on_save:
            return
        
        Utils.call(self.on_save, self.all())
    
    def destroy(self)-> None:
        if not self.on_destroy:
            return
        
        Utils.call(self.on_destroy, self)