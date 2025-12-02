import typing as t
import typing_extensions as te
import dataclasses as dt
import pydantic as tp
import enum, functools, uuid, datetime, hashlib
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.types import (
    PositiveInt, EventCallback, UniqueIdUuid, UniqueAlias
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    _CONF, _convert, _data, _str, _utils, _validate
)

# BEGIN: Data Classes
dataclass = dt.dataclass

@functools.wraps(dt.dataclass)
def model_class(cls=None, /, **kwargs):
    kwargs['init']=True
    kwargs['kw_only']=True
    return dt.dataclass(cls, **kwargs)

@functools.wraps(dt.field)
def model_field(**kwargs):
    options = _data().all_except(kwargs, *_CONF['data_classes']['kwargs'].keys())
    kwargs = _data().only_with(kwargs, *_CONF['data_classes']['kwargs'].keys())
    kwargs = _data().combine(kwargs, {'metadata': {'_options': options}}, recursive=True)
    return dt.field(**kwargs)

def model_method(**kwargs):
    def decorator(func):        
        setattr(func, '__metadata__', kwargs)
        return func
    return decorator
# END: Data Classes

# BEGIN: Generic - Definitions
SENTINEL: object = object()
SENTINEL_TS: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
SENTINEL_ID: str = f'{str(id(SENTINEL))}_{str(SENTINEL_TS.strftime('%Y-%m-%dT%H:%M:%S'))}.{SENTINEL_TS.microsecond * 1000:09d}Z'
SENTINEL_HASH: str = hashlib.md5(SENTINEL_ID.encode()).hexdigest()

@dataclass(frozen=True)
class Separator:
    char: str = model_field(default='-', init=True)
    times: PositiveInt = model_field(default=50, init=True)

    def make(self) -> str:
        return self.char * self.times

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
    
    def dispatchable(self) -> bool:
        return self.is_(self.READY, self.QUEUED)
    
    def dispatched(self) -> bool:
        return not self.dispatchable()
    
    def finished(self) -> bool:
        return not self.dispatchable()
    
    def cancellable(self) -> bool:
        return not self.dispatched()
    
    def cancelable(self) -> bool:
        return self.cancelable()

@dataclass(kw_only=True)
class BaseModel:
    def __dataclass_field(self, name: str, key: str = '', default: t.Any = None) -> t.Any:
        attr = self.__dataclass_fields__.get(name)

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
        attr = super().__getattribute__(name)
        
        if name in ['__class__', '__dataclass_fields__', '__dataclass_field']:
            return attr
        
        is_callable = _validate().is_callable(attr)
        is_protected_method = is_callable and _data().get(attr, '__metadata__.protected') == True
        is_hidden_field = not is_callable and self.__dataclass_field(name, 'metadata._options.hidden') == True

        if is_protected_method and not _validate().callable_called_within_hierarchy(self, '__getattribute__'):
            # _utils().dump(_convert().as_callable_caller_segments(self, '__getattribute__'))
            raise RuntimeError(f'Protected method [{name}] cannot be called externally.')
        elif is_hidden_field and not _validate().callable_called_within_hierarchy(self, '__getattribute__'):
            raise RuntimeError(f'Hidden attribute [{name}] cannot be accessed externally.')

        return attr
# END: Generic - Definitions

# BEGIN: Events
@dataclass(kw_only=True, frozen=True)
class StatusChangedEvent:
    related: t.Any
    previous: GenericStatus
    current: GenericStatus
# END: Events

# BEGIN: Mixins
@dataclass(kw_only=True)
class IdMixin:
    id: UniqueIdUuid = model_field(default_factory=uuid.uuid4, init=False, repr=True, frozen=True)
    alias: t.Optional[UniqueAlias] = model_field(default=None, init=True, repr=True, frozen=True)

@dataclass(kw_only=True)
class CallableMixin:
    @model_method(protected=True)
    def _caller_get_config(self, *args, **kwargs):
        kwargs = _data().append(kwargs, '__caller.bind.annotations', self)        
        
        return [args, kwargs]
    
    @model_method(protected=True)
    def _caller_make_call(self, callback: t.Optional[t.Callable], *args, **kwargs) -> t.Any:
        if not callback:
            return
        
        args, kwargs = self._caller_get_config(*args, **kwargs)

        return _utils().call(callback, *args, **kwargs)

@dataclass(kw_only=True)
class StatusMixin:
    status: GenericStatus = model_field(default=GenericStatus.READY, init=False, repr=True, protected=True)
    on_status_change: t.Optional[EventCallback] = model_field(default=None, init=True, repr=True, frozen=True)
    
    @model_method(protected=True)
    def _set_status(self, status: GenericStatus) -> te.Self:
        if self.status == status:
            return self
        
        previous = self.status
        self.status = status

        if not self.on_status_change:
            return self

        kwargs = {
            '__caller': {
                'bind': {
                    'annotations': [StatusChangedEvent(related=self, previous=previous, current=status)],
                },
            },
        }
    
        _utils().call(self.on_status_change, **kwargs)

        return self
# END: Mixins