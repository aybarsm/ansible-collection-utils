import typing as t
from pydantic import PositiveInt
import typing_extensions as te
import asyncio
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.types import (
    ENUMERATABLE, MappingImmutable, EventCallback, UniqueIdInt, UniqueAlias, PositiveFloat,
    TaskResult, EventCallback, 
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.definitions import (
    BaseModel, Field, GenericStatus, StatusMixin
)
from ansible_collections.aybarsm.utils.plugins.module_utils.tools.task import Task, TaskGroup
from ansible_collections.aybarsm.utils.plugins.module_utils.tools.collection import Collection
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Convert, Data, Utils

TaskCollectionIdentifier = t.Union[UniqueIdInt, UniqueAlias, Task, asyncio.Task, TaskGroup, ENUMERATABLE[t.Union[UniqueIdInt, UniqueAlias, Task, asyncio.Task, TaskGroup]]]

class TaskCollection(Collection[Task]):
    context: t.Optional[t.Any] = None

    def __init__(
        self,
        tasks: ENUMERATABLE[Task] = [],
        context: t.Optional[t.Any] = None,
    ):
        super().__init__(tasks)
        self.context = context
        
    def append(self, task: Task | ENUMERATABLE[Task]) -> te.Self:
        return self.__append_or_prepend(True, task)
        
    def prepend(self, task: Task | ENUMERATABLE[Task]) -> te.Self:
        return self.__append_or_prepend(False, task)
    
    def push(self, task: Task) -> te.Self:
        return self.append(task)
    
    def add(self, task: Task) -> te.Self:
        return self.append(task)

    # def find(
    #     self,
    #     identifier: UniqueIdInt | UniqueAlias | Task | asyncio.Task,
    # ) -> t.Optional[Task]:
    #     index = self.find_index(identifier)

    #     return None if index == None else self.items[index]
    
    # def get(
    #     self,
    #     identifier: ENUMERATABLE[UniqueIdInt | Task | TaskGroup] | TaskGroup,
    # ) -> tuple[Task, ...]:
    #     indexes = self.get_index(identifier)

    #     return tuple([self.items[index] for index in self.indexes() if index in indexes]) #type: ignore
    
    # def find_index(
    #     self,
    #     identifier: UniqueIdInt | UniqueAlias | Task | asyncio.Task,
    # ) -> t.Optional[int]:
    #     identifier = self.resolve_identifier(identifier)

    #     if isinstance(identifier, int):
    #         return self.first_index(lambda task: task.id == identifier)
    #     elif isinstance(identifier, TaskAlias):
    #         return self.first_index(lambda task: task.alias == identifier)
    #     elif isinstance(identifier, TaskGroupId):
    #         return self.first_index(lambda task: task.group.id == identifier)
        
    # def get_index(
    #     self,
    #     identifier: ENUMERATABLE[UniqueIdInt | Task | TaskGroup] | TaskGroup,
    # ) -> tuple[int, ...]:
    #     identifier = self.resolve_identifier(identifier) #type: ignore

    #     return self.where_index(lambda task: task.group.id == identifier)
    
    def get_ids(self) -> list[UniqueIdInt]:
        return self.pluck('id')
    
    def get_aliases(self) -> list[UniqueAlias]:
        return self.pluck('alias')
    
    def get_results(self) -> list[TaskResult]:
        return self.pluck('result')
    
    def get_mapped_results(self) -> MappingImmutable[UniqueIdInt, TaskResult]:
        return MappingImmutable(
            self.each(lambda task, idx, ret: Data.set_(ret, str(task.id), task.result), {})
        )
    
    def get_dispatchers(self) -> list[t.Callable]:
        return self.pluck('dispatch')

    def get_groups(self) -> list[TaskGroup]:
        return self.pluck('group', unique=True, filled=True)
    
    def get_group_ids(self) -> list[UniqueIdInt]:
        return self.pluck('group.id', unique=True, filled=True)
    
    def get_group_aliases(self) -> list[UniqueAlias]:
        return self.pluck('group.alias', unique=True, filled=True)
    
    @staticmethod
    def resolve_retrieval_callback(
        identifier: TaskCollectionIdentifier,
    ) -> t.Callable:
        done = set()
        ret = []

        for ident in Convert.to_iterable(identifier):
            if isinstance(ident, int):
                key, val = 'task.id', ident
            elif isinstance(ident, str):
                key, val = 'task.alias', ident
            elif isinstance(ident, Task):
                key, val = 'task.id', ident.id
            elif isinstance(ident, asyncio.Task):
                key, val = 'task.id', int(ident.get_name())
            elif isinstance(ident, TaskGroup):
                key, val = 'task.group.id', ident.id
            
            key_done = f'{key}_{str(val)}'
            if key_done in key_done:
                continue
            
            ret.append(lambda task: getattr(task, key) == val)
            done.add(key_done)
        
        return lambda task: any(ret)
    
    def __append_or_prepend(self, is_append: bool, task: Task | ENUMERATABLE[Task]) -> te.Self:
        for item in Convert.to_iterable(task):
            if is_append:
                super().append(item)
            else:
                super().prepend(item)

        self.__validate_uniqueness()

        return self
    
    def __validate_uniqueness(self) -> None:
        if self.empty():
            return
        
        aliases = self.get_aliases()
        if len(aliases) != len(set(aliases)):
            raise RuntimeError(f'Task aliases must be unique.')

class TaskCollectionDispatchable(TaskCollection, StatusMixin):
    def __init__(
        self,
        tasks: ENUMERATABLE[Task] = [],
        context: t.Optional[t.Any] = None,
        timeout: t.Optional[PositiveFloat] = None,
        abort_on_failed: bool = True,
        on_status_change: t.Optional[EventCallback] = None,
    ):
        super().__init__(tasks, context)
        
        self._timeout = timeout
        self._abort_on_failed: bool = abort_on_failed
        self._on_status_change: t.Optional[EventCallback] = on_status_change
    
    @property
    def timeout(self) -> t.Optional[PositiveFloat]:
        self._timeout
    
    @property
    def abort_on_failed(self) -> bool:
        return self._abort_on_failed
    
    def abort(self) -> te.Self:
        if not self.status.abortable():
            raise RuntimeError('Only running task collection can be aborted.')
        
        self._set_status(GenericStatus.ABORTED)

        return self