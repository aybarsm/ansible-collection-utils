import typing as T
import time, threading
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.fluent import Fluent
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.task import Task, TaskCollection, JobCollection

class Pipeline(object):
    def __init__(self, tasks: T.Optional[TaskCollection] = None):
        self.data: Fluent = Fluent()
        self.tasks: TaskCollection

        if tasks:
            self.tasks = tasks
        else:
            self.tasks = TaskCollection()
        
        self._lock = threading.Lock()
        self.jobs: JobCollection = self.tasks.get_job_collection()
    
    def add_task(self, task: Task) -> "Pipeline":
        self.tasks.add(task)
        return self