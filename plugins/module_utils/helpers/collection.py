import typing as T
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    __data, __validate, __utils, __pydash,
)

Data = __data()
Utils = __utils()
Validate = __validate()

class Collection(object):
    on_save: T.Optional[T.Callable] = None
    on_destroy: T.Optional[T.Callable] = None

    def __init__(self, items: list[T.Any]|tuple[T.Any]|set[T.Any] = []):
        self.items: list[T.Any] = list(items).copy()
    
    def map(self, callback: T.Callable) -> None:
        for idx_, val_ in self.items:
            self.items[idx_] = Utils.call(callback, val_, idx_)
    
    def each(self, callback: T.Callable) -> None:
        for idx_, val_ in self.items:
            res = Utils.call(callback, val_, idx_, self)
            if res == False:
                break
    
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
    
    def sort_by(self, callback: str|T.Callable, reverse: bool = False) -> T.Any:
        return Collection(self.pydash().sort_by(self.all(), callback, reverse))
    
    def sort(self, callback: str|T.Callable, reverse: bool = False) -> T.Any:
        return self.sort_by(callback, reverse)
    
    def append(self, value: T.Any, **kwargs) -> None:
        self.items = Data.append(self.items, '', value, **kwargs)
    
    def prepend(self, value: T.Any, **kwargs) -> None:
        self.items = Data.prepend(self.items, '', value, **kwargs)
    
    def push(self, value: T.Any, **kwargs) -> None:
        self.append(value, **kwargs)
    
    def pop(self) -> T.Any:
        return self.items.pop()

    def pluck(self, key: str) -> list[T.Any]:
        return self.pydash().pluck(self.all(), key)
    
    def all(self)-> list:
        return self.items.copy()
    
    def empty(self)-> bool:
        return Validate.blank(self.items)
    
    def not_empty(self)-> bool:
        return not self.empty()
    
    def pydash(self):
        return __pydash().collections
    
    def copy(self):
        return Collection(self.all())
    
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