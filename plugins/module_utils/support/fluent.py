### BEGIN: Imports
from ansible_collections.aybarsm.utils.plugins.module_utils.support.definitions import (
    t, te, dt, T, 
    Model, field, CallableMixin, 
)
### END: Imports
### BEGIN: ImportManager
from ansible_collections.aybarsm.utils.plugins.module_utils.support.convert import (
	Convert_as_copied, Convert_to_items, Convert_to_primitive,
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.data import (
	Data_all_except, Data_append, Data_combine,
	Data_first, Data_get, Data_has,
	Data_last, Data_only_with, Data_prepend,
	Data_reject, Data_set, Data_where, 
    Data_unset, 
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.validate import (
	Validate_blank, Validate_contains, Validate_filled,
)
### END: ImportManager

@dt.dataclass(init=True)
class FluentImmutable(BaseModel, t.Generic[T]):
    data: T = field(default_factory=dict, init=True)
    
    def get(self, key: str, default: t.Any = None) -> t.Any:
        return Convert_as_copied(Data_get(self.data, key, default))
    
    def get_filled(self, key: str, default, **kwargs) -> t.Any:
        if not self.has(key):
            return default
        
        ret = self.get(key)
        return default if not Validate_filled(ret, **kwargs) else ret
    
    def has(self, key: str) -> bool:
        return Data_has(self.data, key)
    
    def filled(self, key: str) -> bool:
        return Validate_filled(self.get(key))

    def blank(self, key: str) -> bool:
        return Validate_blank(self.get(key))
    
    def contains(self, key: str, *args, **kwargs) -> bool:
        return Validate_contains(self.get(key, []), *args, **kwargs)
    
    def empty(self) -> bool:
        return Validate_blank(self.data)
    
    def not_empty(self) -> bool:
        return not self.empty()

    def where(self, callback: t.Callable, default: t.Any = None, **kwargs) -> t.Any:
        return Data_where(self.data, callback, default, **kwargs)
    
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
    
    def all(self) -> dict[t.Any, t.Any]:
        return Convert_to_primitive(self.data, as_dict=True)
    
    def copy(self) -> te.Self:
        return self.__class__(Convert_as_copied(self.data))

    def __dict__(self) -> dict[t.Any, t.Any]:
        return self.all()
    
    def __copy__(self) -> te.Self:
        return self.copy()

    def __deepcopy__(self) -> te.Self:
        return self.copy()

@dt.dataclass(init=True)
class Fluent(FluentImmutable, CallableMixin):
    on_save: t.Optional[t.Callable] = field(default=None, init=True)
    on_destroy: t.Optional[t.Callable] = field(default=None, init=True)    
    
    def get(self, key: str, default: t.Any = None) -> t.Any:
        return Data_get(self.data, key, default)
    
    def set(self, key: str, value: t.Any) -> T:
        Data_set(self.data, key, value)
        return self.data
    
    def increase(self, key: str, start: int|float = 0, step: int|float = 1) -> int | float:
        current = self.get(key, start)
        current += step
        self.set(key, current)
        return current
    
    def decrease(self, key: str, start: int|float = 0, step: int|float = 1) -> int | float:
        current = self.get(key, start)
        current -= step
        self.set(key, current)
        return current
    
    def unset(self, key: str) -> T:
        Data_unset(self.data, key)
        return self.data
    
    def forget(self, key: str) -> T:
        return self.unset(key)
    
    def append(self, key: str, *args: t.Any, **kwargs) -> T:
        self.data = Data_append(self.data, key, *args, **kwargs)
        return self.data

    def prepend(self, key: str, *args: t.Any, **kwargs) -> T:
        self.data = Data_prepend(self.data, key, *args, **kwargs)
        return self.data
    
    def pop(self, key: str, default: t.Any = None) -> t.Any:
        current = list(self.get(key, []))
        
        if Validate_filled(current):
            ret = current.pop()
        else:
            ret = default
        
        self.set(key, current)

        return ret    

    def keys(self) -> list[str]:
        return [str(key_) for key_ in self.data.keys()]
    
    def items(self, key_name: str = 'key', value_name: str = 'value',)-> list[dict[str, t.Any]]:
        return Convert_to_items(self.all(), key_name, value_name)

    def only_with(self, *args, **kwargs):
        return Data_only_with(self.all(), *args, **kwargs)
    
    def all_except(self, *args, **kwargs):
        return Data_all_except(self.all(), *args, **kwargs)
    
    def combine(self, data: t.Mapping, key: str, **kwargs)-> None:
        if Validate_blank(key):
            self.data = Data_combine(self.all(), dict(data), **kwargs)
        else:
            self.set(key, Data_combine(self.get(key, {}), dict(data), **kwargs))
    
    def save(self) -> None:
        self._caller_make_call(self.on_save)
    
    def destroy(self) -> None:
        self._caller_make_call(self.on_destroy)