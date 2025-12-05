### BEGIN: Imports
from ansible_collections.aybarsm.utils.plugins.module_utils.support.definitions import (
    t, te, T, 
    ENUMERATABLE, Sentinel, 
)
### END: Imports
### BEGIN: ImportManager
from ansible_collections.aybarsm.utils.plugins.module_utils.support.data import (
	Data_append, Data_collections, Data_pluck,
	Data_prepend, Data_where,
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.utils import (
	Utils_call,
)
### END: ImportManager

class Collection(t.Generic[T]):
    on_save: t.Optional[t.Callable] = None
    on_destroy: t.Optional[t.Callable] = None

    def __init__(self, items: ENUMERATABLE[T] = []):
        self.items: list[T] = list(items).copy()
        self.__sentinel: str = Sentinel.hash
    
    @property
    def sentinel(self) -> str:
        return self.__sentinel
    
    def map(self, callback: t.Callable) -> t.Self:
        for idx in self.indexes():
            self.items[idx] = Utils_call(callback, self.items[idx], idx)
        
        return self
    
    def each(self, callback: t.Callable, initial: t.Any = None) -> t.Any:
        ret = initial
        for idx_, val_ in enumerate(self.items):
            ret = Utils_call(callback, val_, idx_, ret, self)
            if ret == self.sentinel:
                break
        
        return ret
    
    def where_index(self, callback: t.Callable, **kwargs) -> tuple[int, ...]:
        kwargs['key'] = True
        return tuple(Data_where(self.items, callback, [], **kwargs))
    
    def where_index_single(self, callback: t.Callable, **kwargs) -> t.Optional[int]:
        kwargs['key'] = True
        return Data_where(self.items, callback, None, **kwargs)
    
    def where(self, callback: t.Callable, **kwargs) -> tuple[T, ...]:
        return tuple([self.items[idx] for idx in self.indexes() if idx in self.where_index(callback, **kwargs)])
    
    def where_single(self, callback: t.Callable, **kwargs) -> t.Optional[T]:
        if not any([kwargs.get('first', False), kwargs.get('last', False)]):
            raise RuntimeError('No single keyword provided')
        
        key = self.where_index_single(callback, **kwargs)
        return None if key == None else self.items[key]
    
    def reject(self, callback: t.Callable, **kwargs) -> tuple[T, ...]:
        kwargs['negate'] = True
        return self.where(callback, **kwargs)

    def first(self, callback: t.Optional[t.Callable] = None, **kwargs) -> t.Optional[T]:
        if callback == None:
            return self.items[0] if self.not_empty() else None
            
        kwargs['first'] = True
        kwargs['last'] = False
        return self.where_single(callback, **kwargs)
    
    def last(self, callback: t.Optional[t.Callable] = None, **kwargs) -> t.Optional[T]:
        if callback == None:
            return self.items[-1] if self.not_empty() else None
        
        kwargs['first'] = False
        kwargs['last'] = True
        return self.where_single(callback, **kwargs)
    
    def reject_index(self, callback: t.Callable, **kwargs) -> tuple[int, ...]:
        kwargs['negate'] = True
        return self.where_index(callback, **kwargs)

    def first_index(self, callback: t.Callable, **kwargs) -> t.Optional[int]:
        kwargs['first'] = True
        kwargs['last'] = False
        return self.where_index_single(callback, **kwargs)
    
    def last_index(self, callback: t.Callable, **kwargs) -> t.Optional[int]:
        kwargs['first'] = False
        kwargs['last'] = True
        return self.where_index_single(callback, **kwargs)
    
    def sort_by(self, callback: str | t.Callable, reverse: bool = False) -> te.Self:
        return self.__class__(Data_collections().sort_by(self.all(), callback, reverse))
    
    def sort(self, callback: str | t.Callable, reverse: bool = False) -> t.Any:
        return self.sort_by(callback, reverse)
    
    def append(self, value: T, **kwargs) -> None:
        self.items = list(Data_append(self.items, '', value, **kwargs))
    
    def prepend(self, value: T, **kwargs) -> None:
        self.items = list(Data_prepend(self.items, '', value, **kwargs))
    
    def push(self, value: T, **kwargs) -> None:
        self.append(value, **kwargs)
    
    def add(self, value: T, **kwargs) -> None:
        self.append(value, **kwargs)
    
    def pop(self) -> T:
        return self.items.pop()

    def pluck(self, key: str, **kwargs) -> list[t.Any]:
        return Data_pluck(self.all(), key, **kwargs)
    
    def all(self)-> list[T]:
        return list(self.items.copy())
    
    def count(self) -> int:
        return len(self.items)
    
    def empty(self)-> bool:
        return self.count() == 0
    
    def not_empty(self)-> bool:
        return not self.empty()
    
    def copy(self) -> te.Self:
        return self.__class__(self.all())
    
    def indexes(self) -> set[int]:
        return set(range(0, len(self.items))) if self.not_empty() else set()
    
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