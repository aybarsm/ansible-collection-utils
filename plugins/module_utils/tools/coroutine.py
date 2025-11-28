import typing as t
import typing_extensions as te
import asyncio
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.types import (
    ENUMERATABLE, PositiveInt, CommonStatus, SENTINEL_HASH
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Convert, Utils

CoroCallbackResult = t.Any
CoroContext = t.Any
CoroPoolSize = PositiveInt
CoroCallbackUniqueId = str
CoroCallback = t.Callable[..., CoroCallbackResult]
CoroAbortWhenCallback = t.Callable[..., bool]
CoroGetUniqueCallbackIdCallback = t.Callable[..., CoroCallbackUniqueId]

class Concurrent:
    def __init__(
            self,
            tasks: TaskCollection,
            size: t.Optional[CoroPoolSize] = None,
            abort_when: t.Optional[CoroAbortWhenCallback] = None,
            get_id_using: t.Optional[CoroGetUniqueCallbackIdCallback] = None,
        ):
        self.__tasks: TaskCollection = tasks
        self.__context: t.Optional[CoroContext] = context
        self.__size: CoroPoolSize = size or len(self.__callbacks)
        self.__status: CommonStatus = CommonStatus.NOT_EXECUTED
        self.__abort_when: t.Optional[CoroAbortWhenCallback] = abort_when
        self.__get_id_using: t.Optional[CoroGetUniqueCallbackIdCallback] = get_id_using

        self.__semaphore: asyncio.Semaphore
        self.__queued: set[asyncio.Task]
        self.__finished: list[asyncio.Task]
        self.__results: dict[str, t.Any]

    @property
    def callbacks(self) -> set[CoroCallback]:
        return self.__callbacks
    
    @property
    def context(self) -> t.Optional[CoroContext]:
        return self.__context
    
    @property
    def size(self) -> PositiveInt:
        return self.__size
    
    @property
    def status(self) -> CommonStatus:
        return self.__status
    
    @property
    def abort_when(self) -> t.Optional[CoroAbortWhenCallback]:
        return self.__abort_when
    
    @property
    def get_id_using(self) -> t.Optional[CoroGetUniqueCallbackIdCallback]:
        return self.__get_id_using
    
    @property
    def count(self) -> PositiveInt:
        return len(self.callbacks)
    
    @property
    def empty(self) -> bool:
        return self.count == 0
    
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
    
    def add_callback(self, callback: CoroCallback | ENUMERATABLE[CoroCallback]) -> te.Self:
        for cb in Convert.to_iterable(callback):
            self.__callbacks.add(cb)

        return self
    
    def __get_call_conf(self) -> dict:
        return {'__caller': {'bind': {'annotation': {type(self): self}}}}
    
    def __generate_results(self) -> list[t.Any]:
        return [self.__results[str(idx)] if str(idx) in self.__results else CommonStatus.NOT_EXECUTED for idx in range(0, len(self.__callbacks))]
    
    def __should_abort(self, result = t.Any) -> bool:
        if not self.abort_when:
            return False
        
        return Utils.call(self.abort_when, result, **self.__get_call_conf())

    def __prepare_execution(self) -> None:
        self.__semaphore = asyncio.Semaphore(self.size)
        self.__pending = set()
        self.__finished = []
        self.__results = {}

        for idx, callback in enumerate(self.__callbacks):
            task = asyncio.create_task(coro=self.__sem_task(callback), name=str(idx))
            self.__pending.add(task)
    
    async def __sem_task(self, callback: t.Callable) -> t.Any:
        async with self.__semaphore:
            if asyncio.iscoroutinefunction(callback):
                result = await callback()
            else:
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(None, callback)
            
            if self.__should_abort(result):
                self.__status = CommonStatus.ABORTED

            return result
    
    async def run(self) -> list[t.Any]:
        if not self.callbacks:
            raise ValueError("Callbacks cannot be empty")
        
        if self.running:
            raise RuntimeError('Concurrency already running.')
        
        self.__prepare_execution()
        self.__status = CommonStatus.RUNNING

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