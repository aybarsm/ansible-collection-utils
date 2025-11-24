import typing as T
from dataclasses import dataclass
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.collection import Collection

TaskId = str
TaskAlias = str
TaskAsync = bool
TaskPoll = float
TaskResult = T.Any
TaskStartResult = T.Any
TaskCallback = T.Callable[[TaskId, T.Optional[object]], TaskResult]
TaskOnStartCallback = T.Optional[T.Callable[[TaskId, TaskStartResult, T.Optional[object]], None]]
TaskOnStatusCallback = T.Callable[[TaskId, T.Optional[object]], bool]
TaskOnCompleteCallback = T.Optional[T.Callable[[TaskId, T.Optional[object]], None]]

@dataclass
class Task:
    id: TaskId
    alias: TaskAlias
    result: TaskResult
    start_result: TaskStartResult
    callback: TaskCallback
    on_start: TaskOnStartCallback
    on_status: TaskOnStatusCallback
    on_complete: TaskOnCompleteCallback
    is_async: TaskAsync
    poll: TaskPoll = 0.01

    def __post_init__(self):
        if self.poll < 0.01:
            raise ValueError('Poll delay value cannot be lower than 0.01')
        
        if self.is_async and self.on_status:
            raise ValueError('Async task cannot have on_status callback')
        
        self.id = 'job_' + str(id(self.callback))

class TaskCollection(Collection[Task]):
    pass