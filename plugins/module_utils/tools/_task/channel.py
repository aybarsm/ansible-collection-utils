import typing as t
import typing_extensions as te
import asyncio
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.types import (
    ENUMERATABLE, PositiveInt, PositiveFloat, CommonStatus
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Utils
from ansible_collections.aybarsm.utils.plugins.module_utils.tools.task import Task
from ansible_collections.aybarsm.utils.plugins.module_utils.tools._task.collection import (
    TaskCollectionContext, TaskCollection
)

TaskChannelSize = PositiveInt
TaskChannelTimeout = PositiveFloat

class TaskChannel(TaskCollection):
    def __init__(
            self,
            tasks: ENUMERATABLE[Task] = [],
            size: t.Optional[TaskChannelSize] = None,
            context: t.Optional[TaskCollectionContext] = None,
            timeout: t.Optional[TaskChannelTimeout] = None,
            abort_on_failed: bool = True,
        ):
        super().__init__(tasks, context)

        self.__size: t.Optional[TaskChannelSize] = size
        self.__timeout: t.Optional[TaskChannelTimeout] = timeout
        self.__status: CommonStatus = CommonStatus.NOT_EXECUTED
        
        self.__abort_on_failed: bool = abort_on_failed
    
    @property
    def size(self) -> TaskChannelSize:
        if self.__size:
            return self.__size
        else:
            return self.count()

    @property
    def timeout(self) -> t.Optional[TaskChannelTimeout]:
        self.__timeout
    
    @property
    def status(self) -> CommonStatus:
        return self.__status
    
    @property
    def abort_on_failed(self) -> bool:
        return self.__abort_on_failed
    
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
        return self.status in [CommonStatus.FINISHED, CommonStatus.ABORTED]
    
    @property
    def aborted(self) -> bool:
        return self.status == CommonStatus.ABORTED

    def dispatch(self) -> te.Self:
        asyncio.run(self.__run())
        
        return self
    
    def __on_task_done(self, coro_task: asyncio.Task) -> None:
        task = self.find(coro_task)
        if not task:
            raise RuntimeError(f'Coroutine delviered task [{coro_task.get_name()}] not found.')
        
        if task.failed:
            if self.abort_on_failed and not self.aborted:
                self.__status = CommonStatus.ABORTED
        
        if not task.executed and self.aborted:
            task.cancel()
    
    async def __run(self) -> None:
        if self.running:
            raise RuntimeError('Concurrency already running.')
        
        semaphore: asyncio.Semaphore = asyncio.Semaphore(self.size)
        pending: set[asyncio.Task] = set()
        
        self.__status = CommonStatus.RUNNING

        for task in self.items:
            coro_task = asyncio.create_task(
                coro=Utils.call_semaphore(semaphore, task.dispatch), 
                name=task.id,
                context=self.context
            )

            coro_task.add_done_callback(
                lambda task_done: self.__on_task_done(task_done)
            )
            
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

            if self.aborted:
                for coro_task in pending:
                    coro_task.cancel()
                    self.__on_task_done(coro_task)
                
                try:
                    await asyncio.gather(*pending)
                except asyncio.CancelledError:
                    pass

                break
        
        if self.running:
            self.__status = CommonStatus.FINISHED