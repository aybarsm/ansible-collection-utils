import typing as t
import asyncio
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.types import (
    ENUMERATABLE, PositiveInt, CommonStatus
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Utils
from ansible_collections.aybarsm.utils.plugins.module_utils.tools.data_id_factory import DataIdFactory

AbortWhenCallback = t.Callable[..., bool]

class Concurrent:
    def __init__(
            self,
            callbacks: ENUMERATABLE[t.Callable], 
            size: t.Optional[PositiveInt] = None,
            abort_when: t.Optional[AbortWhenCallback] = None,
        ):
        if not callbacks:
            raise ValueError("Callbacks cannot be empty")
        
        self.__callbacks: set[t.Callable] = set(callbacks)
        self.__size: PositiveInt = size or len(self.__callbacks)
        self.__status: CommonStatus = CommonStatus.NOT_EXECUTED
        self.__abort_when: t.Optional[AbortWhenCallback] = abort_when

        self.__semaphore: asyncio.Semaphore
        self.__pending: set[asyncio.Task]
        self.__results: dict[str, t.Any]

    @property
    def size(self) -> PositiveInt:
        return self.__size
    
    @property
    def status(self) -> CommonStatus:
        return self.__status
    
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
    
    @property
    def abort_when(self) -> t.Optional[AbortWhenCallback]:
        return self.__abort_when
    
    def __get_call_conf(self) -> dict:
        return {'__caller': {'bind': {'annotation': {type(self): self}}}}
    
    def __generate_results(self) -> list[t.Any]:
        return [self.__results[str(idx)] if str(idx) in self.__results else CommonStatus.NOT_EXECUTED for idx in range(0, len(self.__callbacks))]
    
    def __prepare_execution(self) -> None:
        self.__semaphore = asyncio.Semaphore(self.size)
        self.__pending = set()
        self.__results = {}
    
    async def __sem_task(self, callback: t.Callable) -> t.Any:
        async with self.__semaphore:
            if asyncio.iscoroutinefunction(callback):
                result = await callback()
            else:
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, callback)
            
            if self.abort_when:
                should_abort = Utils.call(self.abort_when, result, **self.__get_call_conf())
                if should_abort:
                    self.__status = CommonStatus.ABORTED
            
            return result
    
    async def run(self) -> list[t.Any]:
        if self.running:
            raise RuntimeError('Concurrency already running.')
        
        self.__prepare_execution()
        self.__status = CommonStatus.RUNNING

        for idx, callback in enumerate(self.__callbacks):
            task = asyncio.create_task(coro=self.__sem_task(callback), name=str(idx))
            self.__pending.add(task)

        while self.__pending:
            done, self.__pending = await asyncio.wait(self.__pending, return_when=asyncio.FIRST_COMPLETED)
            
            for task in done:
                try:
                    self.__results[task.get_name()] = await task
                except asyncio.CancelledError:
                    pass

            if self.aborted:
                for task in self.__pending:
                    task.cancel()
                await asyncio.gather(*self.__pending, return_exceptions=True)
                break
        
        if self.running:
            self.__status = CommonStatus.FINISHED
        
        return self.__generate_results()

class WaitConcurrent(Concurrent):
    def run(self) -> list[t.Any]:
        return asyncio.run(super().run())