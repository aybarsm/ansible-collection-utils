import typing as t
import typing_extensions as te
import dataclasses as dt
import pydantic as tp
import enum, functools, uuid
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.types import (
    PydanticBaseModel, EventCallback, UniqueIdUuid, UniqueAlias
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    _CONF, _convert, _data, _utils, _validate
)

# BEGIN: Generic - Definitions
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
# END: Generic - Definitions

# BEGIN: Pydantic
def __wrap_pydantic_field(*args, **kwargs):
    for extra, default in _data().get(_CONF, 'pydantic.extras', {}).items():
        _data().set_(kwargs, f'json_schema_extra.{extra}', kwargs.pop(extra, default))
    
    return [args, kwargs]

@functools.wraps(tp.PrivateAttr)
def wrapped_pydantic_privateattr(*args, **kwargs) -> t.Any:
    # args, kwargs = __wrap_pydantic_field(*args, **kwargs)
    return tp.PrivateAttr(*args, **kwargs)

@functools.wraps(tp.Field)
def wrapped_pydantic_field(*args, **kwargs) -> t.Any:
    args, kwargs = __wrap_pydantic_field(*args, **kwargs)
    return tp.Field(*args, **kwargs)

PrivateAttr = wrapped_pydantic_privateattr
Field = wrapped_pydantic_field
computed_field = tp.computed_field

class Ignored:
    pass

class BaseModel(PydanticBaseModel):
    id: UniqueIdUuid = Field(default_factory=uuid.uuid4, init=False, repr=False, frozen=True)
    alias: t.Optional[UniqueAlias] = Field(default=None, init=True, repr=False, frozen=True)
    
    model_config = tp.ConfigDict(extra='allow')
    __pydantic_post_init__ = 'model_post_init'

    @property
    def __protected_attributes__(self) -> tuple[str, ...]:
        ret = [attr for attr in self.__pydantic_fields__.keys() if _data().get(self.__pydantic_fields__, f'{attr}.json_schema_extra.protected') == True]
        ret.extend(list(self.__private_attributes__.keys()))
        return tuple(ret)

    def model_post_init(self, context: t.Any):
        self.__pydantic_configure_protected__()
    
    def __pydantic_configure_protected__(self) -> None:
        for attr in self.__protected_attributes__:
            if attr in self.__pydantic_fields__:
                self.__pydantic_fields__[attr].frozen = True

            if attr not in self.__pydantic_setattr_handlers__:
                self.__pydantic_setattr_handlers__[attr] = self.__pydantic_protected_attr_set_handler__ #type: ignore

    def __pydantic_protected_attr_set_handler__(self, container: "BaseModel", attr: str, value: t.Any):
        if not _validate().callable_called_within_hierarchy(container, '__setattr__'):
            raise ValueError(f'Attribute [{attr}] is protected. Cannot be modified externally.')
    
        object.__setattr__(container, attr, value)
    
# END: Pydantic

# BEGIN: Mixins
class CallableMixin:
    def _caller_get_config(self, *args, **kwargs):
        kwargs = _data().append(kwargs, '__caller.bind.annotations', self)        
        
        return [args, kwargs]

    def _caller_make_call(self, callback: t.Optional[t.Callable], *args, **kwargs) -> t.Any:
        if not callback:
            return
        
        args, kwargs = self._caller_get_config(*args, **kwargs)

        return _utils().call(callback, *args, **kwargs)

class StatusMixin(CallableMixin):
    status: GenericStatus = Field(default=GenericStatus.READY, init=False, repr=True, protected=True)
    on_status_change: t.Optional[EventCallback] = Field(default=GenericStatus.READY, init=True, repr=True, frozen=True)

    def _set_status(self, status: GenericStatus) -> te.Self:
        kwargs = {
            'status_previous': self.status,
            'status_current': status,
        }

        if kwargs['status_previous'] == status:
            return self
        
        self.status = status

        self._caller_make_call(self.on_status_change, **kwargs)

        return self
# END: Mixins