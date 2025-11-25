import time, threading, asyncio, functools
import typing as T
from dataclasses import dataclass
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    __utils
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.fluent import Fluent
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.collection import Collection

Utils = __utils()

TaskGroupId = str
TaskGroupConcurrency = T.Optional[int]

TaskId = str
TaskAlias = str
TaskAsync = bool
TaskPoll = float
TaskResult = T.Any
TaskStartResult = T.Any
TaskCallback = T.Callable[["Task", "Queue"], TaskResult]
TaskOnStartCallback = T.Optional[T.Callable[["Task", "Queue"], None]]
TaskOnStatusCallback = T.Optional[T.Callable[["Task", "Queue"], bool]]
TaskOnCompleteCallback = T.Optional[T.Callable[["Task", "Queue"], None]]

JobActive = bool
JobFailed = bool
JobCompleted = bool

JobCollectionAll = set[TaskId]
JobCollectionConcurrency = T.Optional[int]
JobCollectionQueued = set[TaskId]
JobCollectionActive = list[TaskId]
JobCollectionFailed = set[TaskId]
JobCollectionCompleted = set[TaskId]

@dataclass
class TaskGroup:
    id: TaskGroupId
    concurrency: TaskGroupConcurrency = None

@dataclass
class Task:
    id: TaskId
    alias: TaskAlias
    result: TaskResult
    start_result: TaskStartResult
    callback: TaskCallback
    on_start: TaskOnStartCallback = None
    on_status: TaskOnStatusCallback = None
    on_complete: TaskOnCompleteCallback = None
    is_async: TaskAsync = False
    poll: TaskPoll = 0.01
    group: T.Optional[TaskGroup] = None

    def __post_init__(self):
        if self.poll < 0.01:
            raise ValueError('Poll delay value cannot be lower than 0.01')
        
        if self.is_async and self.on_status:
            raise ValueError('Async task cannot have on_status callback')
        
        self.id = 'job_' + str(id(self.callback))
    
    def dispatch(self, queue: "Queue") -> None:
        if self.on_start:
            self.start_result = Utils.call(self.callback, self, queue)

            Utils.call(self.on_start, self, queue)
        else:
            self.result = Utils.call(self.callback, self, queue)
    
    def get_status(self, queue: "Queue") -> T.Optional[bool]:
        if self.on_status:
            return Utils.call(self.on_status, self, queue)
        else:
            return None
    
    def completed(self, queue: "Queue") -> None:
        if self.on_complete:
            Utils.call(self.on_complete, self, queue)
    
    def has_on_start_callback(self) -> bool:
        return self.on_start != None
    
    def has_on_status_callback(self) -> bool:
        return self.on_status != None

    def has_on_complete_callback(self) -> bool:
        return self.on_complete != None

@dataclass
class TaskCollection(Collection[Task]):
    pass

    def get(self, identifier: TaskId|TaskAlias|TaskGroupId) -> T.Optional[Task] | T.Optional["TaskCollection"]:
        if isinstance(identifier, TaskId):
            return self.get_by_id(identifier)
        elif isinstance(identifier, TaskAlias):
            return self.get_by_alias(identifier)
        elif isinstance(identifier, TaskGroupId):
            return self.get_by_group(identifier)
    
    def get_by_id(self, identifier: TaskId) -> T.Optional[Task]:
        return self.first(lambda task: task.id == identifier)    
    
    def get_by_alias(self, identifier: TaskAlias) -> T.Optional[Task]:
        return self.first(lambda task: task.alias == identifier)
    
    def get_by_group(self, identifier: TaskGroupId) -> T.Optional["TaskCollection"]:
        tasks = self.where(lambda task: task.group.id == identifier)
        
        if len(tasks) > 0:
            return TaskCollection(tasks) #type: ignore
        else:
            return None

    def get_ids(self) -> list[TaskId]:
        return list(self.pluck('id'))
    
    def get_job_collection(self) -> "JobCollection":
        return JobCollection(set(self.get_ids()))

@dataclass
class JobCollection:
    all: JobCollectionAll
    queued: JobCollectionQueued = set()
    active: JobCollectionActive = []
    failed: JobCollectionFailed = set()
    completed: JobCollectionCompleted = set()
    concurrent: JobCollectionConcurrency = None

    def __post_init__(self):
        if not self.has_jobs():
            raise ValueError('No jobs provided')
        
        if self.concurrent and self.concurrent < 1:
            raise ValueError('Job concurrency value cannot be lower than 1')
        
        self.queued = set(self.all)
        self.active = []
        self.failed = set()
        self.completed = set()
    
    def has_jobs(self) -> bool:
        return len(self.all) > 0

    def has_active(self) -> bool:
        return len(self.active) > 0
    
    def has_failed(self) -> bool:
        return len(self.failed) > 0
    
    def has_completed(self) -> bool:
        return len(self.completed) > 0

class Queue(object):
    def __init__(self, tasks: T.Optional[TaskCollection] = None):
        self.data: Fluent = Fluent()

        if tasks:
            self.tasks = tasks
        else:
            self.tasks = TaskCollection()

        self._lock: threading.Lock
        self.jobs: JobCollection
    
    def add_task(self, task: Task) -> "Queue":
        self.tasks.add(task)

        return self
    
    def run(self) -> None:
        if self.tasks.empty():
            return
        
        self._lock = threading.Lock()
        self.jobs = self.tasks.get_job_collection()
        
        self._start()

        with self._lock:
            if not self.jobs.has_active():
                return
            
        self._poll()
    
