import typing as t
import typing_extensions as te
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.types import (
    ENUMERATABLE, CommonStatus
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Convert, Utils
from ansible_collections.aybarsm.utils.plugins.module_utils.tools.collection import Collection
from ansible_collections.aybarsm.utils.plugins.module_utils.tools.coroutine import WaitConcurrent

TaskId = str
TaskAlias = t.Optional[str]
TaskGroup = t.Optional[str]
TaskResult = t.Any
TaskCallback = t.Callable[..., TaskResult]
TaskOnFinallyCallback = t.Callable[..., None]

TaskChannelSize = int

class Task:
    def __init__(
        self,
        callback: TaskCallback,
        alias: TaskAlias = None, 
        group: TaskGroup = None,
        on_finally: t.Optional[TaskOnFinallyCallback] = None
    ):
        self.__callback: TaskCallback = callback
        self.__alias: TaskAlias = alias
        self.__group: TaskGroup = group
        self.__on_finally: t.Optional[TaskOnFinallyCallback] = on_finally

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
    def group(self) -> TaskGroup:
        return self.__group
    
    @property
    def on_finally(self) -> t.Optional[TaskOnFinallyCallback]:
        return self.__on_finally

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
        return self.status in [CommonStatus.FINISHED, CommonStatus.FAILED]
    
    @property
    def failed(self) -> bool:
        return self.status == CommonStatus.FAILED

    def dispatch(self) -> te.Self:
        if self.dispatched or self.finished:
            return self.result
        
        self.__status = CommonStatus.RUNNING
        call_conf = {'__caller': {'bind': {'annotation': {Task: self}}}}
        try:
            self.__result = Utils.call(self.callback, **call_conf)
            self.__status = CommonStatus.FINISHED
        except Exception as e:
            self.__result = e
            self.__status = CommonStatus.FAILED
        finally:
            if self.on_finally:
                Utils.call(self.on_finally, **call_conf)
        
        return self

class TaskCollection(Collection[Task]):
    def __init__(self, tasks: ENUMERATABLE[Task]):
        super().__init__(tasks)

        if self.empty():
            return
        
        aliases = self.get_aliases()
        if len(aliases) != len(set(aliases)):
            raise RuntimeError(f'Task aliases must be unique.')

    def __validate_unique_task_alias(self, task: Task) -> None:
        if self.get(task.alias) != None:
            raise RuntimeError(f'Task with [{task.alias}] alias already exists.')
        
    def append(self, task: Task) -> None:
        self.__validate_unique_task_alias(task)
        super().append(task)
    
    def prepend(self, task: Task) -> None:
        self.__validate_unique_task_alias(task)
        super().prepend(task)
    
    def push(self, task: Task) -> None:
        self.append(task)
    
    def add(self, task: Task) -> None:
        self.append(task)

    def get(self, identifier: str | Task | TaskId | TaskAlias | TaskGroup) -> t.Optional[Task | list[Task]]:
        if isinstance(identifier, str):
            identifier = TaskId(identifier)

        if isinstance(identifier, Task):
            return self.get_by_id(identifier.id)
        elif isinstance(identifier, TaskId):
            return self.get_by_id(identifier)
        elif isinstance(identifier, TaskAlias):
            return self.get_by_alias(identifier)
        elif isinstance(identifier, TaskGroup):
            return self.get_by_group(identifier)
    
    def get_by_id(self, identifier: TaskId) -> t.Optional[Task]:
        return self.first(lambda task: task.id == identifier)
    
    def get_by_alias(self, identifier: TaskAlias) -> t.Optional[Task]:
        return self.first(lambda task: task.alias == identifier)
    
    def get_by_group(self, identifier: TaskGroup) -> list[Task]:
        return self.where(lambda task: task.group == identifier)
    
    def get_ids(self) -> list[TaskId]:
        return self.pluck('id')
    
    def get_aliases(self) -> list[TaskAlias]:
        return self.pluck('alias')
    
    def get_results(self) -> list[TaskResult]:
        return self.pluck('result')
    
    def get_dispatchers(self) -> list[t.Callable]:
        return self.pluck('dispatch')

    def get_groups(self) -> list[TaskGroup]:
        return [group for group in set(self.pluck('group')) if group]

class TaskChannel(TaskCollection):
    def __init__(
            self,
            tasks: ENUMERATABLE[Task] = [],
            size: t.Optional[TaskChannelSize] = None,
            abort_on_failed: bool = True,
        ):
        self.__size: t.Optional[TaskChannelSize] = size
        self.__concurrent: WaitConcurrent
        self.__abort_on_failed: bool = abort_on_failed

        super().__init__(tasks)
    
    @property
    def size(self) -> t.Optional[TaskChannelSize]:
        if hasattr(self, '__concurrent'):
            return self.__concurrent.size
        else:
            return self.__size
    
    @property
    def running(self) -> bool:
        return hasattr(self, '__concurrent') and self.__concurrent.running
    
    @property
    def finished(self) -> bool:
        return hasattr(self, '__concurrent') and self.__concurrent.finished

    def dispatch(self) -> list[TaskResult]:        
        abort_when = None
        if self.__abort_on_failed:
            abort_when = lambda task: task.failed
        
        results = WaitConcurrent(self.get_dispatchers(), self.size, abort_when).run()
        
        return results

class TaskPipeline(Collection[Task | TaskChannel]):
    pass