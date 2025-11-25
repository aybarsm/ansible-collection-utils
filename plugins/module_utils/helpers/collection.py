import typing as T
from typing_extensions import Self

from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    __data, __utils, 
)

CollectionItem = T.TypeVar('CollectionItem')
Data = __data()
Utils = __utils()

class Collection(T.Generic[CollectionItem]):
    on_save: T.Optional[T.Callable] = None
    on_destroy: T.Optional[T.Callable] = None

    def __init__(self, items: list[CollectionItem] | tuple[CollectionItem] | set[CollectionItem] = []):
        self.items: list[CollectionItem] = list(items).copy()
    
    def map(self, callback: T.Callable) -> None:
        for idx_, val_ in enumerate(self.items):
            self.items[idx_] = Utils.call(callback, val_, idx_)
    
    def each(self, callback: T.Callable) -> None:
        for idx_, val_ in enumerate(self.items):
            res = Utils.call(callback, val_, idx_, self)
            if res == False:
                break
    
    def where(self, callback: T.Callable, **kwargs) -> list[CollectionItem]:
        return list(Data.where(self.all(), callback, [], **kwargs))
    
    def reject(self, callback: T.Callable, **kwargs) -> list[CollectionItem]:
        return list(Data.reject(self.all(), callback, [], **kwargs))

    def first(self, callback: T.Callable, **kwargs) -> T.Optional[CollectionItem]:
        return Data.first(self.all(), callback, None, **kwargs)
    
    def last(self, callback: T.Callable, **kwargs) -> T.Optional[CollectionItem]:
        return Data.last(self.all(), callback, None, **kwargs)
    
    def where_key(self, callback: T.Callable, **kwargs) -> list[int]:
        kwargs['key'] = True
        return list(Data.where(self.all(), callback, [], **kwargs))
    
    def reject_key(self, callback: T.Callable, **kwargs) -> list[int]:
        kwargs['key'] = True
        return list(Data.reject(self.all(), callback, [], **kwargs))

    def first_key(self, callback: T.Callable, **kwargs) -> T.Optional[int]:
        kwargs['key'] = True
        return Data.first(self.all(), callback, None, **kwargs)
    
    def last_key(self, callback: T.Callable, **kwargs) -> T.Optional[int]:
        kwargs['key'] = True
        return Data.last(self.all(), callback, None, **kwargs)
    
    def sort_by(self, callback: str|T.Callable, reverse: bool = False) -> Self:
        return self.__class__(Data.collections().sort_by(self.all(), callback, reverse))
    
    def sort(self, callback: str|T.Callable, reverse: bool = False) -> T.Any:
        return self.sort_by(callback, reverse)
    
    def append(self, value: CollectionItem, **kwargs):
        self.items = list(Data.append(self.items, '', value, **kwargs))
    
    def prepend(self, value: CollectionItem, **kwargs) -> None:
        self.items = list(Data.prepend(self.items, '', value, **kwargs))
    
    def push(self, value: CollectionItem, **kwargs) -> None:
        self.append(value, **kwargs)
    
    def add(self, value: CollectionItem, **kwargs) -> None:
        self.append(value, **kwargs)
    
    def pop(self) -> CollectionItem:
        return self.items.pop()

    def pluck(self, key: str) -> list[T.Any]:
        return Data.pluck(self.all(), key)
    
    def all(self)-> list[CollectionItem]:
        return list(self.items.copy())
    
    def count(self) -> int:
        return len(self.items)
    
    def empty(self)-> bool:
        return self.count() == 0
    
    def not_empty(self)-> bool:
        return not self.empty()
    
    def copy(self) -> Self:
        return self.__class__(self.all())
    
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