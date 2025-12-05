### BEGIN: Imports
import asyncio
from ansible_collections.aybarsm.utils.plugins.module_utils.support.definitions import (
    t, te,
    ENUMERATABLE, PositiveInt, PositiveFloat, 
    UniqueAlias, EventCallback, GenericStatus,
    dataclass, model_field, 
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support._task.collection import (
    Task, TaskCollectionDispatchable, 
)
### END: Imports
### BEGIN: ImportManager
from ansible_collections.aybarsm.utils.plugins.module_utils.support.utils import (
	Utils_call_semaphore,
)
### END: ImportManager

@dataclass(init=False, kw_only=True)
class TaskChannel(TaskCollectionDispatchable):
    size: t.Optional[PositiveInt] = model_field(default=None, init=True, frozen=True)

    def __init__(
            self,
            alias: t.Optional[UniqueAlias] = None,
            tasks: ENUMERATABLE[Task] = [],
            size: t.Optional[PositiveInt] = None,
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

        self.size: t.Optional[PositiveInt] = size

    def dispatch(self) -> te.Self:
        asyncio.run(self.__run())
        
        return self
    
    def __on_task_done(self, coro_task: asyncio.Task) -> None:
        task = self.find(coro_task)
        if not task:
            raise RuntimeError(f'Coroutine delivered task [{coro_task.get_name()}] not found.')
        
        if task.status.failed() and self.abort_on_failed and self.status.abortable():
            self.abort()
        
        if task.status.cancellable() and self.status.aborted():
            task.cancel()
    
    async def __run(self) -> None:
        if self.status.running():
            raise RuntimeError('Task channel already running.')
        
        semaphore: asyncio.Semaphore = asyncio.Semaphore(self.size if self.size else self.count())
        pending: set[asyncio.Task] = set()
        
        self._set_status(GenericStatus.RUNNING)

        for task in self.items:
            coro_task = asyncio.create_task(
                coro=Utils_call_semaphore(semaphore, task.dispatch, **{'context': self.context}), 
                name=str(task.id)
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