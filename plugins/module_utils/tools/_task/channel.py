import typing as t
import typing_extensions as te
import dataclasses as dt
import asyncio
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.types import (
    ENUMERATABLE, PositiveInt, EventCallback, PositiveFloat
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.definitions import (
    dataclass, model_field, GenericStatus
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Utils
from ansible_collections.aybarsm.utils.plugins.module_utils.tools.task import Task
from ansible_collections.aybarsm.utils.plugins.module_utils.tools._task.collection import TaskCollectionDispatchable

@dataclass(init=False, kw_only=True)
class TaskChannel(TaskCollectionDispatchable):
    size: t.Optional[PositiveInt] = model_field(default=None, init=True, frozen=True)

    def __init__(
            self,
            tasks: ENUMERATABLE[Task] = [],
            size: t.Optional[PositiveInt] = None,
            context: t.Optional[t.Any] = None,
            timeout: t.Optional[PositiveFloat] = None,
            abort_on_failed: bool = True,
        ):
        super().__init__(tasks=tasks, context=context, timeout=timeout, abort_on_failed=abort_on_failed)

        self.size: t.Optional[PositiveInt] = size

    def dispatch(self) -> te.Self:
        asyncio.run(self.__run())
        
        return self
    
    def __on_task_done(self, coro_task: asyncio.Task) -> None:
        task = self.find(coro_task)
        if not task:
            raise RuntimeError(f'Coroutine delivered task [{coro_task.get_name()}] not found.')
        
        if task.status.failed() and self.abort_on_failed and self.status.abortable:
            self.abort()
        
        if task.status.cancellable() and self.status.aborted():
            task.cancel()
    
    async def __run(self) -> None:
        if self.status.running():
            raise RuntimeError('Concurrency already running.')
        
        semaphore: asyncio.Semaphore = asyncio.Semaphore(self.size if self.size else self.count())
        pending: set[asyncio.Task] = set()
        
        self._set_status(GenericStatus.RUNNING)

        for task in self.items:
            coro_task = asyncio.create_task(
                coro=Utils.call_semaphore(semaphore, task.dispatch), 
                name=str(task.id),
                context=self.context
            )
            
            task.queue()

            coro_task.add_done_callback(self.__on_task_done)
            
            pending.add(coro_task)

        while pending:
            done, pending = await asyncio.wait(
                pending, 
                timeout=self.timeout, 
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in done:
                try:
                    await task
                except asyncio.CancelledError:
                    pass

            if self.status.aborted():
                for coro_task in pending:
                    coro_task.cancel()
                    self.__on_task_done(coro_task)
                
                try:
                    await asyncio.gather(*pending)
                except asyncio.CancelledError:
                    pass

                break
        
        if self.status.running():
            self._set_status(GenericStatus.COMPLETED)