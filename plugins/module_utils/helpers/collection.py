import typing as t
from typing_extensions import Self
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.types import (
    T, ENUMERATABLE
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    __data, __utils, 
)

Data = __data()
Utils = __utils()

class Collection(t.Generic[T]):
    on_save: t.Optional[t.Callable] = None
    on_destroy: t.Optional[t.Callable] = None

    def __init__(self, items: ENUMERATABLE):
        self.items: list[T] = list(items).copy()
    
    def map(self, callback: t.Callable) -> None:
        for idx_, val_ in enumerate(self.items):
            self.items[idx_] = Utils.call(callback, val_, idx_)
    
    def each(self, callback: t.Callable) -> None:
        for idx_, val_ in enumerate(self.items):
            res = Utils.call(callback, val_, idx_, self)
            if res == False:
                break
    
    def where(self, callback: t.Callable, **kwargs) -> list[T]:
        return list(Data.where(self.all(), callback, [], **kwargs))
    
    def reject(self, callback: t.Callable, **kwargs) -> list[T]:
        return list(Data.reject(self.all(), callback, [], **kwargs))

    def first(self, callback: t.Callable, **kwargs) -> t.Optional[T]:
        return Data.first(self.all(), callback, None, **kwargs)
    
    def last(self, callback: t.Callable, **kwargs) -> t.Optional[T]:
        return Data.last(self.all(), callback, None, **kwargs)
    
    def where_key(self, callback: t.Callable, **kwargs) -> list[int]:
        kwargs['key'] = True
        return list(Data.where(self.all(), callback, [], **kwargs))
    
    def reject_key(self, callback: t.Callable, **kwargs) -> list[int]:
        kwargs['key'] = True
        return list(Data.reject(self.all(), callback, [], **kwargs))

    def first_key(self, callback: t.Callable, **kwargs) -> t.Optional[int]:
        kwargs['key'] = True
        return Data.first(self.all(), callback, None, **kwargs)
    
    def last_key(self, callback: t.Callable, **kwargs) -> t.Optional[int]:
        kwargs['key'] = True
        return Data.last(self.all(), callback, None, **kwargs)
    
    def sort_by(self, callback: str | t.Callable, reverse: bool = False) -> Self:
        return self.__class__(Data.collections().sort_by(self.all(), callback, reverse))
    
    def sort(self, callback: str | t.Callable, reverse: bool = False) -> t.Any:
        return self.sort_by(callback, reverse)
    
    def append(self, value: T, **kwargs) -> None:
        self.items = list(Data.append(self.items, '', value, **kwargs))
    
    def prepend(self, value: T, **kwargs) -> None:
        self.items = list(Data.prepend(self.items, '', value, **kwargs))
    
    def push(self, value: T, **kwargs) -> None:
        self.append(value, **kwargs)
    
    def add(self, value: T, **kwargs) -> None:
        self.append(value, **kwargs)
    
    def pop(self) -> T:
        return self.items.pop()

    def pluck(self, key: str) -> list[t.Any]:
        return Data.pluck(self.all(), key)
    
    def all(self)-> list[T]:
        return list(self.items.copy())
    
    def count(self) -> int:
        return len(self.items)
    
    def empty(self)-> bool:
        return self.count() == 0
    
    def not_empty(self)-> bool:
        return not self.empty()
    
    def copy(self) -> Self:
        return self.__class__(self.all())
    
    def indexes(self) -> set[int]:
        return set(range(0, len(self.items) - 1))
    
    def keys(self) -> set[int]:
        return self.indexes()
    
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