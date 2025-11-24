import typing as T
import asyncio, functools
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    __convert
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.fluent import Fluent
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.task import Task, TaskCollection

Convert = __convert()

class Pipeline(object):
    def __init__(self, tasks: T.Optional[TaskCollection] = None):
        self.data: Fluent = Fluent()
        self.tasks: TaskCollection

        if tasks:
            self.tasks = tasks
        else:
            self.tasks = TaskCollection()
    
    def add_task(self, task: Task) -> "Pipeline":
        self.tasks.add(task)
        return self

    async def _execute_task_logic(self, task: Task, previous_result=None):
        if task.is_async:
            result = await task.callback(task.id, self)
        else:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, task.id, self)

        if task.on_status:
            while True:
                loop = asyncio.get_running_loop()
                is_ready = await loop.run_in_executor(None, functools.partial(task.on_status, task.id, self))
                
                if is_ready:
                    break
                
                await asyncio.sleep(task.poll)

        if task.on_complete:
            if asyncio.iscoroutinefunction(task.on_complete):
                await task.on_complete(task.id, self)
            else:
                task.on_complete(task.id, self)
                
        return result

    async def run_pipeline(self):
        results = []
        last_result = None
        
        for task in self.tasks:
            last_result = await self._execute_task_logic(task, last_result)
            results.append(last_result)
            
        return results

    def run_background(self):
        return asyncio.create_task(self.run_pipeline())

    async def wait(self):
        return await self.run_pipeline()