import typing as t
import typing_extensions as te
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.types import (
    ENUMERATABLE, CommonStatus, PositiveInt, immutable_data
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Convert, Utils

TaskId = str
TaskAlias = t.Optional[str]
TaskResult = t.Any
TaskCallback = t.Callable[..., TaskResult]
TaskEventCallback = t.Callable[..., None]

TaskGroupId = str
TaskGroupConcurrent = PositiveInt

@immutable_data
class TaskGroup:
    id: TaskGroupId
    concurrent: t.Optional[TaskGroupConcurrent] = None

class Task:
    def __init__(
        self,
        callback: TaskCallback,
        alias: TaskAlias = None, 
        group: t.Optional[TaskGroup] = None,
        on_finally: t.Optional[TaskEventCallback] = None,
        on_cancel: t.Optional[TaskEventCallback] = None,
        on_uncancel: t.Optional[TaskEventCallback] = None,
    ):
        self.__callback: TaskCallback = callback
        self.__alias: TaskAlias = alias
        self.__group: t.Optional[TaskGroup] = group
        self.__on_finally: t.Optional[TaskEventCallback] = on_finally
        self.__on_cancel: t.Optional[TaskEventCallback] = on_cancel
        self.__on_uncancel: t.Optional[TaskEventCallback] = on_uncancel

        self.__id: TaskId = Convert.as_id(self.callback, 'task_')
        self.__status: CommonStatus = CommonStatus.NOT_EXECUTED
        self.__result: TaskResult = CommonStatus.NOT_EXECUTED

        if not self.__alias:
            self.__alias = str(self.__id)
        
    @property
    def callback(self) -> TaskCallback:
        return self.__callback

    @property
    def id(self) -> TaskId:
        return self.__id

    @property
    def alias(self) -> TaskAlias:
        return self.__alias
    
    @property
    def group(self) -> t.Optional[TaskGroup]:
        return self.__group
    
    @property
    def on_finally(self) -> t.Optional[TaskEventCallback]:
        return self.__on_finally
    
    @property
    def on_cancel(self) -> t.Optional[TaskEventCallback]:
        return self.__on_cancel

    @property
    def on_uncancel(self) -> t.Optional[TaskEventCallback]:
        return self.__on_uncancel

    @property
    def result(self) -> TaskResult:
        return self.__result
    
    @property
    def status(self) -> CommonStatus:
        return self.__status
    
    @property
    def executed(self) -> bool:
        return self.status != CommonStatus.NOT_EXECUTED
    
    @property
    def dispatched(self) -> bool:
        return self.executed
    
    @property
    def running(self) -> bool:
        return self.status == CommonStatus.RUNNING

    @property
    def finished(self) -> bool:
        return self.status in [CommonStatus.FINISHED, CommonStatus.FAILED, CommonStatus.CANCELLED]
    
    @property
    def failed(self) -> bool:
        return self.status == CommonStatus.FAILED
    
    @property
    def cancelled(self) -> bool:
        return self.status == CommonStatus.CANCELLED
    
    @property
    def canceled(self) -> bool:
        return self.cancelled
    
    def cancel(self) -> te.Self:
        if self.executed:
            raise RuntimeError('Only not executed task can be cancelled.')
        
        self.__status = CommonStatus.CANCELLED
        self.__result = CommonStatus.CANCELLED
        Utils.dump(f'Task [{self.id}] :: CANCELLED')
        self.__event_call(self.on_cancel)
        
        return self
    
    def uncancel(self) -> te.Self:
        if not self.cancelled:
            raise RuntimeError('Only cancelled task can be uncancelled.')
        
        self.__status = CommonStatus.NOT_EXECUTED
        self.__result = CommonStatus.NOT_EXECUTED
        self.__event_call(self.on_uncancel)

        return self

    def dispatch(self) -> te.Self:
        if self.dispatched or self.finished:
            return self.result
        
        self.__status = CommonStatus.RUNNING
        try:
            self.__result = Utils.call(self.callback, **self.__get_caller_config())
            self.__status = CommonStatus.FINISHED
        except Exception as e:
            self.__result = e
            self.__status = CommonStatus.FAILED
        finally:
            self.__event_call(self.on_finally)
        
        return self
    
    def __get_caller_config(self) -> dict:
        return {'__caller': {'bind': {'annotation': {Task: self}}}}

    def __event_call(self, callback: t.Optional[t.Callable]) -> None:
        if not callback:
            return
        
        Utils.call(callback, **self.__get_caller_config())