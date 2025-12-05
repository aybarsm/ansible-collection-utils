### BEGIN: Imports
import typing as t
### END: Imports
### BEGIN: ImportManager
from ansible_collections.aybarsm.utils.plugins.module_utils.support.convert import (
	Convert_as_copied, Convert_to_items,
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.data import (
	Data_all_except, Data_append, Data_combine,
	Data_first, Data_get, Data_has,
	Data_last, Data_only_with, Data_prepend,
	Data_pydash, Data_reject, Data_set_,
	Data_where,
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.utils import (
	Utils_call,
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.validate import (
	Validate_blank, Validate_contains, Validate_filled,
)
### END: ImportManager

class Fluent(t.Generic[T]):
    on_save: t.Optional[t.Callable] = None
    on_destroy: t.Optional[t.Callable] = None

    def __init__(self, data: T = {}):
        self.data: T = Convert_as_copied(data)
    
    def get(self, key: str, default: t.Any = None)-> t.Any:
        return Data_get(self.data, key, default)
    
    def get_filled(self, key: str, default, **kwargs)-> t.Any:
        if not self.has(key):
            return default
        
        ret = self.get(key)
        return default if not Validate_filled(ret, **kwargs) else ret
    
    def set(self, key: str, value: t.Any)-> dict:
        Data_set_(self.data, key, value)
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
        Data_forget(self.data, key)
        return self.data
    
    def unset(self, key: str)-> dict:
        return self.forget(key)

    def has(self, key: str)-> bool:
        return Data_has(self.data, key)

    def filled(self, key: str)-> bool:
        return Validate_filled(self.get(key))
    
    def contains(self, key: str, *args, **kwargs)-> bool:
        return Validate_contains(self.get(key, []), *args, **kwargs)

    def blank(self, key: str)-> bool:
        return Validate_blank(self.get(key))
    
    def append(self, key: str, value, **kwargs)-> dict:
        self.data = dict(Data_append(self.data, key, value, **kwargs))
        return self.data

    def prepend(self, key: str, value, **kwargs)-> dict:
        self.data = dict(Data_prepend(self.data, key, value, **kwargs))
        return self.data
    
    def pop(self, key: str, default: t.Any = None) -> t.Any:
        current = list(self.get(key, []))
        
        if Validate_filled(current):
            ret = current.pop()
        else:
            ret = default
        
        self.set(key, current)

        return ret

    def where(self, callback: t.Callable, default: t.Any = None, **kwargs) -> t.Any:
        return Data_where(self.all(), callback, default, **kwargs)
    
    def reject(self, callback: t.Callable, default: t.Any = None, **kwargs) -> t.Any:
        return Data_reject(self.all(), callback, default, **kwargs)

    def first(self, callback: t.Callable, default: t.Any = None, **kwargs) -> t.Any:
        return Data_first(self.all(), callback, default, **kwargs)
    
    def last(self, callback: t.Callable, default: t.Any = None, **kwargs) -> t.Any:
        return Data_last(self.all(), callback, default, **kwargs)
    
    def where_key(self, callback: t.Callable, default: t.Any = None, **kwargs) -> t.Any:
        kwargs['key'] = True
        return self.where(callback, default, **kwargs)
    
    def reject_key(self, callback: t.Callable, default: t.Any = None, **kwargs) -> t.Any:
        kwargs['key'] = True
        return self.reject(callback, default, **kwargs)

    def first_key(self, callback: t.Callable, default: t.Any = None, **kwargs) -> t.Any:
        kwargs['key'] = True
        return self.first(callback, default, **kwargs)
    
    def last_key(self, callback: t.Callable, default: t.Any = None, **kwargs) -> t.Any:
        kwargs['key'] = True
        return self.last(callback, default, **kwargs)

    def keys(self)-> list[str]:
        return [str(key_) for key_ in self.data.keys()]

    def all(self)-> dict:
        return self.data.copy()
    
    def items(self, key_name: str = 'key', value_name: str = 'value',)-> list[dict[str, t.Any]]:
        return Convert_to_items(self.all(), key_name, value_name)

    def only_with(self, *args, **kwargs):
        return Data_only_with(self.all(), *args, **kwargs)
    
    def all_except(self, *args, **kwargs):
        return Data_all_except(self.all(), *args, **kwargs)
    
    def empty(self)-> bool:
        return Validate_blank(self.data)
    
    def not_empty(self)-> bool:
        return not self.empty()
    
    def pydash(self):
        return Data_pydash()
    
    def copy(self):
        return Fluent(self.all())
    
    def combine(self, data: t.Mapping, key: str, **kwargs)-> None:
        if Validate_blank(key):
            self.data = Data_combine(self.all(), dict(data), **kwargs)
        else:
            self.set(key, Data_combine(self.get(key, {}), dict(data), **kwargs))
    
    def __copy__(self):
        return self.copy()

    def __deepcopy__(self):
        return self.copy()
    
    def save(self)-> None:
        if not self.on_save:
            return
        
        Utils_call(self.on_save, self.all())
    
    def destroy(self)-> None:
        if not self.on_destroy:
            return
        
        Utils_call(self.on_destroy, self)