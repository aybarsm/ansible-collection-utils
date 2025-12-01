import typing as t
import typing_extensions as te
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.types import (
    PositiveInt, TaskResult, TaskCallback, EventCallback
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.definitions import (
    BaseModel, Field, PrivateAttr, computed_field, GenericStatus, StatusMixin
)

class TaskGroup(BaseModel):
    is_concurrent: bool = Field(init=True, frozen=True)
    size_concurrent: t.Optional[PositiveInt] = Field(default=None, init=True, frozen=True)

class Task(BaseModel, StatusMixin):
    callback: TaskCallback = Field(init=True, frozen=True)
    group: t.Optional[TaskGroup] = Field(default=None, init=True, frozen=True)
    _result: TaskResult = PrivateAttr(init=False)

    @computed_field
    @property
    def result(self) -> TaskResult:
        return self._result if hasattr(self, '_result') else self.status
    
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

    def dispatch(self) -> te.Self:
        if not self.status.dispatchable():
            return self
        
        self._set_status(GenericStatus.RUNNING)
        try:
            self._result = self._caller_make_call(self.callback)
            self._set_status(GenericStatus.COMPLETED)
        except Exception as e:
            self._result = e
            self._set_status(GenericStatus.FAILED)
        
        return self