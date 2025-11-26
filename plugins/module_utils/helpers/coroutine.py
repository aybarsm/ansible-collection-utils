import typing as t
import asyncio

class Concurrent:
    def __init__(
            self,
            callbacks: list[t.Callable] | tuple[t.Callable] | set[t.Callable], 
            size: t.Optional[int] = None
        ):
        if not callbacks:
            raise ValueError("Callbacks cannot be empty")
        
        if size and size < 1:
            raise ValueError("Concurreny size cannot be lower than 1")
        
        self.__callbacks: set[t.Callable] = set(callbacks)
        self.__size: int = size or len(self.__callbacks)
        self.__is_running: bool = False
        self.__is_finished: bool = False

    @property
    def size(self) -> int:
        return self.__size
    
    @property
    def running(self) -> bool:
        return self.__is_running
    
    @property
    def finished(self) -> bool:
        return self.__is_finished

    async def run(self) -> list[t.Any]:
        if self.__is_running:
            raise RuntimeError('Concurreny already running.')
        
        self.__is_finished = False
        self.__is_running = True

        semaphore = asyncio.Semaphore(self.size)

        async def sem_task(callback: t.Callable) -> t.Any:
            async with semaphore:
                if asyncio.iscoroutinefunction(callback):
                    return await callback()
                else:
                    loop = asyncio.get_running_loop()
                    return await loop.run_in_executor(None, callback)

        results = await asyncio.gather(*(sem_task(callback) for callback in self.__callbacks))

        self.__is_running = False
        self.__is_finished = True

        return results

class WaitConcurrent(Concurrent):
    def run(self) -> list[t.Any]:
        return asyncio.run(super().run())