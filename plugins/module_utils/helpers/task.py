import typing as t
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    __convert, __factory, __utils
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.types import (
    ENUMERATABLE, TaskId, TaskAlias, TaskGroup, TaskResult, TaskCallback, TaskOnFinallyCallback, TaskChannelSize
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.collection import Collection
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.coroutine import WaitConcurrent

Convert = __convert()
Factory = __factory()
Utils = __utils()

class Task:
    def __init__(
        self,
        callback: TaskCallback,
        alias: TaskAlias = None, 
        group: TaskGroup = None,
        on_finally: TaskOnFinallyCallback = None
    ):
        self.__callback: TaskCallback = callback
        self.__alias: TaskAlias = alias
        self.__group: TaskGroup = group
        self.__on_finally: TaskOnFinallyCallback = on_finally

        self.__id: TaskId = Convert.to_md5(f'task_{str(id(self.callback))}_{Factory.ts(mod='long')}')
        self.__result: TaskResult
        self.__is_dispatched: bool = False
        self.__is_finished: bool = False
        self.__is_failed: bool

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
    def on_finally(self) -> TaskOnFinallyCallback:
        return self.__on_finally

    @property
    def result(self) -> TaskResult:
        return self.__result
    
    @property
    def dispatched(self) -> bool:
        return self.__is_dispatched
    
    @property
    def finished(self) -> bool:
        return self.__is_finished
    
    @property
    def failed(self) -> bool:
        if not self.dispatched:
            raise RuntimeError('Task has not dispatched yet to query failure.')
        
        return self.__is_failed

    def dispatch(self) -> TaskResult:
        if self.dispatched or self.finished:
            return self.result
        
        self.__is_dispatched = True
        
        try:
            self.__result = Utils.call(self.callback, self)
        except Exception as e:
            self.__is_failed = True
            self.__result = e
        finally:
            self.__is_finished = True
            if self.on_finally:
                Utils.call(self.on_finally, self)
        
        return self.result

class BaseTaskCollection(Collection[Task]):
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

    def get_groups(self) -> list[TaskGroup]:
        return [group for group in set(self.pluck('group')) if group]

class TaskChannel(BaseTaskCollection):
    def __init__(
            self,
            tasks: list[Task] | tuple[Task] | set[Task] = [],
            size: t.Optional[TaskChannelSize] = None,
        ):
        self.__size: t.Optional[TaskChannelSize] = size
        self.__concurrent: WaitConcurrent

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
        callbacks = []
        
        for idx in self.indexes():
            callbacks.append(self.items[idx].dispatch)
        
        return WaitConcurrent(callbacks, self.size).run()