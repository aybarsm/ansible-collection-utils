import typing as t
import typing_extensions as te
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.types import (
    PositiveInt, GenericUniqueAlias, TaskResult, TaskCallback, EventCallback
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.definitions import (
    BaseModel, Field, computed_field, GenericIdMixin, GenericStatus, StatusMixin
)

class TaskGroup(BaseModel, GenericIdMixin):
    is_concurrent: bool = Field(init=True, protected=True)
    size_concurrent: t.Optional[PositiveInt] = Field(default=None, init=True, protected=True)

class Task(BaseModel, GenericIdMixin, StatusMixin):
    callback: TaskCallback = Field(init=True, frozen=True)
    # alias: t.Optional[GenericUniqueAlias] = Field(default=None, init=True, frozen=True)
    group: t.Optional[TaskGroup] = Field(default=None, init=True, frozen=True)
    # on_status_change: t.Optional[EventCallback] = Field(default=None, init=True, frozen=True)

    # status: GenericStatus = Field(default=GenericStatus.READY, init=True, protected=True)
    # result: TaskResult = Field(require=False, required=False, init=False, protected=True)

    # @computed_field
    # @property
    # def result(self) -> TaskResult:
    #     return "something calculated"

    # def __init__(
    #     self, 
    #     callback: TaskCallback,
    #     alias: t.Optional[GenericUniqueAlias] = None,
    #     group: t.Optional[TaskGroup] = None,
    #     on_status_change: t.Optional[EventCallback] = None,
    # ):
    #     self.callback = callback
    #     self.alias = alias
    #     self.group = group
    #     self.on_status_change = on_status_change
    #     self.status = GenericStatus.READY
        
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