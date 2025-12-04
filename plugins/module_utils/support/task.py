import typing as t
import typing_extensions as te
from ansible_collections.aybarsm.utils.plugins.module_utils.support.types import (
    PositiveInt, TaskResult, TaskCallback
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.definitions import (
    dataclass, BaseModel, model_field, GenericStatus, IdMixin, StatusMixin, CallableMixin
)

@dataclass(kw_only=True)
class TaskGroup(BaseModel, IdMixin):
    is_concurrent: bool = model_field(init=True, frozen=True)
    size_concurrent: t.Optional[PositiveInt] = model_field(default=None, init=True, frozen=True)

@dataclass(kw_only=True)
class Task(BaseModel, IdMixin, StatusMixin, CallableMixin):
    callback: TaskCallback = model_field(init=True, frozen=True)
    group: t.Optional[TaskGroup] = model_field(default=None, init=True, frozen=True)
    result: TaskResult = model_field(default=None, init=False, protected=True)
    
    def queue(self) -> te.Self:
        if not self.status.ready():
            raise RuntimeError('Only ready task can be queued.')
        
        self._set_status(GenericStatus.QUEUED)

        return self

    def cancel(self) -> te.Self:
        if not self.status.cancellable():
            raise RuntimeError('Only ready or queued task can be cancelled.')
        
        self._set_status(GenericStatus.CANCELLED)

        return self
    
    def uncancel(self) -> te.Self:
        if not self.status.cancelled():
            raise RuntimeError('Only cancelled task can be uncancelled.')
        
        self._set_status(GenericStatus.READY)

        return self

    def dispatch(self, context: t.Any = None) -> te.Self:
        if not self.status.dispatchable():
            return self
        
        self._set_status(GenericStatus.RUNNING)
        try:
            self.result = self._caller_make_call(self.callback, **{'context': context})
            self._set_status(GenericStatus.COMPLETED)
        except Exception as e:
            self.result = e
            self._set_status(GenericStatus.FAILED)
        
        return self