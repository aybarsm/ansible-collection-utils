import typing as T
import time, threading, asyncio, functools
from dataclasses import dataclass, field
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    __factory, __utils
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.fluent import Fluent
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.collection import Collection

Factory = __factory()
Utils = __utils()

TaskId = T.Optional[str]
TaskAlias = T.Optional[str]
TaskPoll = float
TaskResult = T.Any
TaskDispatchResult = T.Any
TaskIsDispatched = bool
TaskIsCompleted = bool
TaskCallback = T.Callable[["Task", T.Optional[T.Any]], TaskResult]
TaskOnDispatchCallback = T.Optional[T.Callable[["Task", T.Optional[T.Any]], None]]
TaskOnPollCallback = T.Optional[T.Callable[["Task", T.Optional[T.Any]], bool]]
TaskOnCompleteCallback = T.Optional[T.Callable[["Task", T.Optional[T.Any]], None]]

TaskChannelSize = int
TaskChannelPoll = float
TaskChannelAll = list[TaskId]
TaskChannelActive = list[TaskId]
TaskChannelFailed = set[TaskId]
TaskChannelCompleted = set[TaskId]
TaskChannelResults = dict[TaskId, TaskResult]

@dataclass
class Task:
    callback: TaskCallback
    alias: TaskAlias = None
    on_complete: TaskOnCompleteCallback = None

    _id: TaskId = field(init=False, repr=False)
    _result: TaskResult = field(init=False, repr=False)
    _is_dispatched: TaskIsDispatched = field(default=False, init=True, repr=False)
    _is_completed: TaskIsCompleted = field(default=False, init=True, repr=False)
    _placeholder: str = field(init=False, repr=False)

    @property
    def id(self) -> TaskId:
        return self._id

    @property
    def result(self) -> TaskResult:
        return self._result
    
    @property
    def is_dispatched(self) -> TaskIsDispatched:
        return self._is_dispatched
    
    @property
    def is_completed(self) -> TaskIsCompleted:
        return self._is_completed
    
    def has_result(self) -> bool:
        return hasattr(self, '_result') and getattr(self, '_result', self._placeholder) != self._placeholder
    
    def __post_init__(self):
        self._id = 'job_' + str(id(self.callback))
        self._placeholder = Factory.placeholder(mod='hashed')
    
    async def dispatch(self, send: T.Any = None) -> None:
        if self._dispatched:
            return
        
        self._dispatched = True
        
        self._result = await Utils.call(self.callback, self, send)
        
        await self.__check_status()
    
    async def __check_status(self, send: T.Any = None) -> None:
        while True:
            self._is_completed = self.has_result()

            if self._is_completed:
                await self.__completed(send)
                break

            await asyncio.sleep(1)
    
    async def __completed(self, send: T.Any = None) -> None:
        if not self.on_complete:
            return
        
        Utils.call(self.on_complete, self, send)     

@dataclass
class BaseTaskCollection(Collection[Task]):
    pass

    def get(self, identifier: Task|TaskId|TaskAlias) -> T.Optional[Task]:
        if isinstance(identifier, TaskId):
            return self.get_by_id(identifier)
        elif isinstance(identifier, Task):
            return self.get_by_id(identifier.id)
        elif isinstance(identifier, TaskAlias):
            return self.get_by_alias(identifier)
    
    def get_by_id(self, identifier: TaskId) -> T.Optional[Task]:
        return self.first(lambda task: task.id == identifier)
    
    def get_by_alias(self, identifier: TaskAlias) -> T.Optional[Task]:
        return self.first(lambda task: task.alias == identifier)
    
    def get_ids(self) -> list[TaskId]:
        return self.pluck('id')

@dataclass
class TaskCollection(BaseTaskCollection):
    pass

@dataclass
class TaskChannel(BaseTaskCollection):
    size: TaskChannelSize
    poll: TaskChannelPoll = 1.0

    _lock: threading.Lock = field(init=False, repr=False)
    _all: TaskChannelAll = field(init=False, repr=False)
    _active: TaskChannelActive = field(init=False, repr=False)
    _failed: TaskChannelFailed = field(init=False, repr=False)
    _completed: TaskChannelCompleted = field(init=False, repr=False)
    _results : TaskChannelResults = field(init=False, repr=False)
    _is_aborted : bool = field(default=False, init=True, repr=False)
    pass

    @property
    def results(self) -> TaskChannelResults:
        if self._lock.locked():
            with self._lock:
                return self._results
        else:
            return self._results
    
    def is_aborted(self) -> bool:
        if self._lock.locked():
            with self._lock:
                return self._is_aborted
        else:
            return self._is_aborted
    
    def abort(self) -> None:
        if not self._lock.locked():
            return
        
        with self._lock:
            self._is_aborted = True
    
    def get_active_task_count(self) -> int:
        with self._lock:
            return len(self._active)
        
    def is_running(self) -> bool:
        return self.get_active_task_count() > 0
    
    def has_task_finished(self, task_id: TaskId) -> bool:
        with self._lock:
            return task_id in self._completed or task_id in self._failed
    
    def has_finished(self) -> bool:
        with self._lock:
            return (len(self._completed) + len(self._failed)) == len(self._all)

    def __post_init__(self):
        if self.size < 1:
            raise ValueError('Task channel size value cannot be lower than 1')
        
        if self.poll < 0.01:
            raise ValueError('Task channel poll value cannot be lower than 0.01')
    
    def __task_remove_from_active(self, task_id: TaskId) -> None:
        with self._lock:
            if task_id in self._active:
                self._active.remove(task_id)

    def __task_dispatched(self, task_id: TaskId) -> None:
        with self._lock:
            if task_id not in self._active:
                self._active.append(task_id)
    
    def __task_failed(self, task_id: TaskId) -> None:
        self.__task_remove_from_active(task_id)
        with self._lock:
            self._failed.add(task_id)
    
    def __task_completed(self, task_id: TaskId) -> None:
        self.__task_remove_from_active(task_id)
        with self._lock:
            self._completed.add(task_id)
    
    def wait(self) -> None:
        if self.empty() or self.is_running():
            return

        self.__run()

        if not self.is_running():
            return
    
    def __prepare(self):
        self._lock = threading.Lock()

        with self._lock:
            self._all = self.get_ids()
            self._active = []
            self._failed = set()
            self._completed = set()
            self._results = {}
            self._is_aborted = False

    def __run(self):
        self.__prepare()

        while not self.has_finished():
            with self._lock:
                if self.is_aborted() or not self.has_finished():
                    break

                for task_id in self._all:
                    if self.is_aborted():
                        break
                    
                    if self.has_task_finished(task_id):
                        continue

                    try:
                        task = self.get_by_id(task_id)
                        
                        if not task:
                            self.__task_failed(task_id)
                            continue
                        
                        if not task.is_dispatched:
                            if self.get_active_task_count() == self.size:
                                continue
                            
                            self.results[task_id] = task.dispatch()
                            self.__task_dispatched(task_id)
                        elif task.is_completed:
                            self.__task_completed(task_id)

                    except Exception as e:
                        self.results[task_id] = e
                        self.__task_failed(task_id)
                
                if self.is_running():
                    time.sleep(self.poll)