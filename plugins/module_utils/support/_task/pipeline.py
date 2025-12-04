import typing as t
import typing_extensions as te
from ansible_collections.aybarsm.utils.plugins.module_utils.support.types import (
    ENUMERATABLE, PositiveFloat, EventCallback, UniqueAlias
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.definitions import (
    dataclass, GenericStatus
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.task import Task
from ansible_collections.aybarsm.utils.plugins.module_utils.support._task.collection import TaskCollectionDispatchable
from ansible_collections.aybarsm.utils.plugins.module_utils.support._task.channel import TaskChannel

@dataclass(init=False, kw_only=True)
class TaskPipeline(TaskCollectionDispatchable):
    def __init__(
            self,
            alias: t.Optional[UniqueAlias] = None,
            tasks: ENUMERATABLE[Task] = [],
            context: t.Optional[t.Any] = None,
            timeout: t.Optional[PositiveFloat] = None,
            abort_on_failed: bool = True,
            on_status_change: t.Optional[EventCallback] = None,
        ):
        super().__init__(
            alias=alias,
            tasks=tasks, 
            context=context, 
            timeout=timeout, 
            abort_on_failed=abort_on_failed,
            on_status_change=on_status_change,
        )
    
    def dispatch(self) -> te.Self:
        if self.status.running():
            raise RuntimeError('Task pipeline already running.')
        
        if self.empty():
            raise RuntimeError('No tasks found to dispatch.')
        
        self._set_status(GenericStatus.RUNNING)
        
        for task in self.items:
            if self.status.aborted() and task.status.cancellable():
                task.cancel()
                continue

            if not task.status.dispatchable():
                continue
            
            channel = None
            
            if task.group and task.group.is_concurrent:
                has_size = task.group.size_concurrent and task.group.size_concurrent > 1
                has_length = not task.group.size_concurrent and len(self.get_index(task.group)) > 1
                if has_size or has_length:
                    channel = TaskChannel(
                        alias=str(task.group.id),
                        tasks=self.get(task.group),
                        size=task.group.size_concurrent,
                        context=self.context,
                        timeout=self.timeout,
                        abort_on_failed=self.abort_on_failed,
                        on_status_change=self.on_status_change,
                    ).dispatch()
            
            if not channel:
                task.queue().dispatch(self.context)
            
            is_failed = channel.has_status('failed') if channel else task.status.failed()
            if is_failed and self.abort_on_failed and self.status.abortable():
                self.abort()
        
        if self.status.running():
            self._set_status(GenericStatus.COMPLETED)

        return self