import typing as t
import typing_extensions as te
import dataclasses as dt
import pydantic as tp
import enum, functools, uuid, datetime, hashlib
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.types import (
    EventCallback, UniqueIdUuid, UniqueAlias
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    _CONF, _convert, _data, _str, _utils, _validate
)

# BEGIN: Generic - Definitions
dataclass = dt.dataclass

SENTINEL: object = object()
SENTINEL_TS: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
SENTINEL_ID: str = f'{str(id(SENTINEL))}_{str(SENTINEL_TS.strftime('%Y-%m-%dT%H:%M:%S'))}.{SENTINEL_TS.microsecond * 1000:09d}Z'
SENTINEL_HASH: str = hashlib.md5(SENTINEL_ID.encode()).hexdigest()

class GenericStatus(enum.StrEnum):
    ABORTED = enum.auto()
    CANCELLED = enum.auto()
    COMPLETED = enum.auto()
    FAILED = enum.auto()
    QUEUED = enum.auto()
    READY = enum.auto()
    RUNNING = enum.auto()
    SKIPPED = enum.auto()
    TIMED_OUT = enum.auto()

    def is_(self, *of: "GenericStatus") -> bool:
        return self in of
    
    def not_(self, *of: "GenericStatus") -> bool:
        return self not in of

    def aborted(self) -> bool:
        return self.is_(self.ABORTED)
    
    def cancelled(self) -> bool:
        return self.is_(self.CANCELLED)
    
    def canceled(self) -> bool:
        return self.cancelled()
    
    def completed(self) -> bool:
        return self.is_(self.COMPLETED)
    
    def failed(self) -> bool:
        return self.is_(self.FAILED)

    def queued(self) -> bool:
        return self.is_(self.QUEUED)
    
    def ready(self) -> bool:
        return self.is_(self.READY)
    
    def running(self) -> bool:
        return self.is_(self.RUNNING)
    
    def skipped(self) -> bool:
        return self.is_(self.SKIPPED)
    
    def timed_out(self) -> bool:
        return self.is_(self.TIMED_OUT)
    
    def abortable(self) -> bool:
        return self.running()
    
    def dispatched(self) -> bool:
        return self.not_(self.READY, self.QUEUED)
    
    def dispatchable(self) -> bool:
        return self.ready()
    
    def finished(self) -> bool:
        return self.not_(self.QUEUED, self.RUNNING)
    
    def cancellable(self) -> bool:
        return not self.dispatched()
    
    def cancelable(self) -> bool:
        return self.cancelable()

@functools.wraps(dt.field)
def field(**kwargs):
    options = _data().all_except(kwargs, *_CONF['data_classes']['kwargs'].keys())
    kwargs = _data().only_with(kwargs, *_CONF['data_classes']['kwargs'].keys())
    kwargs = _data().combine(kwargs, {'metadata': {'_options': options}}, recursive=True)
    return dt.field(**kwargs)

def method(**kwargs):
    def decorator(func):        
        setattr(func, '__metadata__', kwargs)
        return func
    return decorator

DUMPS = []

@dataclass
class BaseModel:
    id: UniqueIdUuid = field(default_factory=uuid.uuid4, init=False, repr=False, frozen=True)
    alias: t.Optional[UniqueAlias] = field(default=None, init=True, repr=False, frozen=True)

    def __dataclass_field(self, name: str, key: str = '', default: t.Any = None) -> t.Any:
        attr = super().__getattribute__('__dataclass_fields__').get(name)

        if attr is None:
            return default
        
        if key.strip() == '':
            return attr        

        return _data().get(attr, key, default)
        
    def __delattr__(self, name: str) -> None:
        if self.__dataclass_field(name, 'metadata._options.frozen') == True:
            raise RuntimeError(f'Frozen attribute [{name}] cannot be deleted.')
        
        is_protected = self.__dataclass_field(name, 'metadata._options.protected') == True
        if is_protected and not _validate().callable_called_within_hierarchy(self, '__delattr__'):
            raise RuntimeError(f'Protected attribute [{name}] cannot be deleted externally.')
        
        super().__delattr__(name)
    
    def __setattr__(self, name: str, value: t.Any) -> None:
        is_protected = self.__dataclass_field(name, 'metadata._options.protected') == True
        if is_protected and not _validate().callable_called_within_hierarchy(self, '__setattr__'):
            raise RuntimeError(f'Protected attribute [{name}] cannot be manipulated externally.')
        
        super().__setattr__(name, value)
    
    def __getattribute__(self, name: str) -> t.Any:
        global DUMPS
        attr = super().__getattribute__(name)
        
        if name in ['__class__', '__dataclass_fields__'] or name.endswith('__dataclass_field'):
            return attr
        
        is_protected_method = _validate().is_callable(attr) and _data().get(attr, '__metadata__.protected') == True
        if is_protected_method and not _validate().callable_called_within_hierarchy(self, '__getattribute__'):
            raise RuntimeError(f'Protected method [{name}] cannot be called externally.')

        # is_callable = _validate().is_callable(attr)
        # has_metadata = is_callable and hasattr(attr, '__metadata__')

        

        # if name in super().__getattribute__('__dataclass_fields__'):
        #     is_hidden = self.__dataclass_field(name, '_options.hidden') == True
        #     if is_hidden and not _validate().callable_called_within_hierarchy(self, '__getattribute__'):
        #         raise RuntimeError(f'Hidden attribute [{name}] cannot be accessed externally.')
        # else:
        #     attr = super().__getattribute__(name)
        #     DUMPS.append({'name': name, 'attr': attr, 'callable': _validate().is_callable(attr)})

        return attr

    #     # _utils().dump({'name': name, 'attr': attr})
    #     return attr
        
        # if name.startswith('__'):
        #     return super().__getattribute__(name)
        
        # attr = object.__getattribute__(self, name)
        
        # if not _validate().is_callable(attr):
        #     is_protected = self.__is_field(name, '_options.protected', True)
        #     if is_protected and not _validate().callable_called_within_hierarchy(self, '__getattribute__'):
        #         raise RuntimeError(f'Protected attribute [{name}] cannot be accessed externally.')
            
        #     return attr
        # else:
        #     return attr
        
    #     pass
    
    # def __call__(self, *args: t.Any, **kwds: t.Any) -> t.Any:
    #     _utils().dump({'args': args, 'kwds': kwds})
    #     pass
def model(cls):
    if BaseModel not in cls.__bases__:
        cls.__bases__ = (BaseModel,) + cls.__bases__

    return dt.dataclass(cls)
# END: Generic - Definitions

# BEGIN: Mixins
# class CallableMixin:
#     def _caller_get_config(self, *args, **kwargs):
#         kwargs = _data().append(kwargs, '__caller.bind.annotations', self)        
        
#         return [args, kwargs]

#     def _caller_make_call(self, callback: t.Optional[t.Callable], *args, **kwargs) -> t.Any:
#         if not callback:
#             return
        
#         args, kwargs = self._caller_get_config(*args, **kwargs)

#         return _utils().call(callback, *args, **kwargs)

# class StatusMixin(BaseModel, CallableMixin):
#     status: GenericStatus = field(default=GenericStatus.READY, init=False, repr=True, protected=True)
#     on_status_change: t.Optional[EventCallback] = field(default=None, init=True, repr=True, frozen=True)

#     def _set_status(self, status: GenericStatus) -> te.Self:
#         kwargs = {
#             'status_previous': self.status,
#             'status_current': status,
#         }

#         if kwargs['status_previous'] == status:
#             return self
        
#         self.status = status

#         self._caller_make_call(self.on_status_change, **kwargs)

#         return self
# END: Mixins