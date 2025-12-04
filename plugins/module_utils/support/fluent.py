import typing as t
from ansible_collections.aybarsm.utils.plugins.module_utils.support.types import T
from ansible_collections.aybarsm.utils.plugins.module_utils.aggregator import Kit

class Fluent(t.Generic[T]):
    on_save: t.Optional[t.Callable] = None
    on_destroy: t.Optional[t.Callable] = None

    def __init__(self, data: T = {}):
        self.data: T = Kit.Convert().as_copied(data)
    
    def get(self, key: str, default: t.Any = None)-> t.Any:
        return Kit.Data().get(self.data, key, default)
    
    def get_filled(self, key: str, default, **kwargs)-> t.Any:
        if not self.has(key):
            return default
        
        ret = self.get(key)
        return default if not Kit.Validate().filled(ret, **kwargs) else ret
    
    def set(self, key: str, value: t.Any)-> dict:
        Kit.Data().set_(self.data, key, value)
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
        Kit.Data().forget(self.data, key)
        return self.data
    
    def unset(self, key: str)-> dict:
        return self.forget(key)

    def has(self, key: str)-> bool:
        return Kit.Data().has(self.data, key)

    def filled(self, key: str)-> bool:
        return Kit.Validate().filled(self.get(key))
    
    def contains(self, key: str, *args, **kwargs)-> bool:
        return Kit.Validate().contains(self.get(key, []), *args, **kwargs)

    def blank(self, key: str)-> bool:
        return Kit.Validate().blank(self.get(key))
    
    def append(self, key: str, value, **kwargs)-> dict:
        self.data = dict(Kit.Data().append(self.data, key, value, **kwargs))
        return self.data

    def prepend(self, key: str, value, **kwargs)-> dict:
        self.data = dict(Kit.Data().prepend(self.data, key, value, **kwargs))
        return self.data
    
    def pop(self, key: str, default: t.Any = None) -> t.Any:
        current = list(self.get(key, []))
        
        if Kit.Validate().filled(current):
            ret = current.pop()
        else:
            ret = default
        
        self.set(key, current)

        return ret

    def where(self, callback: t.Callable, default: t.Any = None, **kwargs) -> t.Any:
        return Kit.Data().where(self.all(), callback, default, **kwargs)
    
    def reject(self, callback: t.Callable, default: t.Any = None, **kwargs) -> t.Any:
        return Kit.Data().reject(self.all(), callback, default, **kwargs)

    def first(self, callback: t.Callable, default: t.Any = None, **kwargs) -> t.Any:
        return Kit.Data().first(self.all(), callback, default, **kwargs)
    
    def last(self, callback: t.Callable, default: t.Any = None, **kwargs) -> t.Any:
        return Kit.Data().last(self.all(), callback, default, **kwargs)
    
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
        return Kit.Convert().to_items(self.all(), key_name, value_name)

    def only_with(self, *args, **kwargs):
        return Kit.Data().only_with(self.all(), *args, **kwargs)
    
    def all_except(self, *args, **kwargs):
        return Kit.Data().all_except(self.all(), *args, **kwargs)
    
    def empty(self)-> bool:
        return Kit.Validate().blank(self.data)
    
    def not_empty(self)-> bool:
        return not self.empty()
    
    def pydash(self):
        return Kit.Data().pydash()
    
    def copy(self):
        return Fluent(self.all())
    
    def combine(self, data: t.Mapping, key: str, **kwargs)-> None:
        if Kit.Validate().blank(key):
            self.data = Kit.Data().combine(self.all(), dict(data), **kwargs)
        else:
            self.set(key, Kit.Data().combine(self.get(key, {}), dict(data), **kwargs))
    
    def __copy__(self):
        return self.copy()

    def __deepcopy__(self):
        return self.copy()
    
    def save(self)-> None:
        if not self.on_save:
            return
        
        Kit.Utils().call(self.on_save, self.all())
    
    def destroy(self)-> None:
        if not self.on_destroy:
            return
        
        Kit.Utils().call(self.on_destroy, self)