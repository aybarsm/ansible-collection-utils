from typing import Any, Mapping
from ansible_collections.aybarsm.utils.plugins.module_utils.tools import Validate, Data, Helper

class Fluent():
    _ = Data.pydash()

    def __init__(self, data: Mapping[Any, Any] = {}):
        self.data = dict(data).copy()
    
    def get(self, key: str, default: Any = None)-> Any:
        return self._.get(self.data, key, default)
    
    def set(self, key: str, value: Any)-> dict:
        self._.set_(self.data, key, value)
        return self.data
    
    def forget(self, key: str)-> dict:
        self._.unset(self.data, key)
        return self.data
    
    def unset(self, key: str)-> dict:
        return self.forget(key)

    def has(self, key: str)-> bool:
        return self._.has(self.data, key)

    def filled(self, key: str)-> bool:
        return Validate.filled(self.get(key))

    def blank(self, key: str)-> bool:
        return Validate.blank(self.get(key))
    
    def append(self, key: str, value, **kwargs)-> dict:
        self.data = dict(Data.append(self.data, key, value, **kwargs))
        return self.data

    def prepend(self, key: str, value, **kwargs)-> dict:
        self.data = dict(Data.prepend(self.data, key, value, **kwargs))
        return self.data

    def all(self)-> dict:
        return self.data.copy()
    
    def pydash(self):
        return self._
    
    def copy(self):
        return Fluent(self.all())
    
    def __copy__(self):
        return self.copy()

    def __deepcopy__(self):
        return self.copy()