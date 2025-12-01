import typing as t
import typing_extensions as te
import asyncio
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.types import (
    ENUMERATABLE, MappingImmutable, EventCallback, PositiveFloat,
    TaskId, TaskAlias, TaskResult, EventCallback, 
    TaskGroupId, TaskCollectionId, TaskCollectionAlias, 
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.definitions import (
    GenericIdMixin, GenericStatus, StatusMixin
)
from ansible_collections.aybarsm.utils.plugins.module_utils.tools.task import Task, TaskGroup
from ansible_collections.aybarsm.utils.plugins.module_utils.tools.collection import Collection
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Convert, Data, Utils

class TaskCollection(GenericIdMixin, Collection[Task]):
    def __init__(
        self,
        tasks: ENUMERATABLE[Task] = [],
        context: t.Optional[t.Any] = None,
        alias: t.Optional[TaskCollectionAlias] = None,
    ):
        super().__init__(tasks)

        self.context: t.Optional[t.Any] = context
        self._alias: t.Optional[TaskCollectionAlias] = alias
        
        self.__validate_uniqueness()

    @property
    def alias(self) -> t.Optional[TaskCollectionAlias]:
        return self._alias
        
    def append(self, task: Task | ENUMERATABLE[Task]) -> te.Self:
        return self.__append_or_prepend(True, task)
        
    def prepend(self, task: Task | ENUMERATABLE[Task]) -> te.Self:
        return self.__append_or_prepend(False, task)
    
    def push(self, task: Task) -> te.Self:
        return self.append(task)
    
    def add(self, task: Task) -> te.Self:
        return self.append(task)

    def find(
        self,
        identifier: str | Task | TaskId | TaskAlias | TaskGroup | TaskGroupId | asyncio.Task,
    ) -> t.Optional[Task]:
        index = self.find_index(identifier)

        return None if index == None else self.items[index]
    
    def get(
        self,
        identifier: TaskGroup | TaskGroupId,
    ) -> tuple[Task, ...]:
        indexes = self.find_index(identifier)

        return tuple([self.items[index] for index in self.indexes() if index in indexes]) #type: ignore
    
    def find_index(
        self,
        identifier: str | Task | TaskId | TaskAlias | TaskGroup | TaskGroupId | asyncio.Task,
    ) -> t.Optional[int]:
        identifier = self.resolve_identifier(identifier)

        if isinstance(identifier, TaskId):
            return self.first_index(lambda task: task.id == identifier)
        elif isinstance(identifier, TaskAlias):
            return self.first_index(lambda task: task.alias == identifier)
        elif isinstance(identifier, TaskGroupId):
            return self.first_index(lambda task: task.group.id == identifier)
        
    def get_index(
        self,
        identifier: TaskGroup | TaskGroupId,
    ) -> tuple[int, ...]:
        identifier = self.resolve_identifier(identifier) #type: ignore

        return self.where_index(lambda task: task.group.id == identifier)
    
    def get_ids(self) -> list[TaskId]:
        return self.pluck('id')
    
    def get_aliases(self) -> list[TaskAlias]:
        return self.pluck('alias')
    
    def get_results(self) -> list[TaskResult]:
        return self.pluck('result')
    
    def get_mapped_results(self) -> MappingImmutable[TaskId, TaskResult]:
        return MappingImmutable(
            self.each(lambda task, idx, ret: Data.set_(ret, task.id, task.result), {})
        )
    
    def get_dispatchers(self) -> list[t.Callable]:
        return self.pluck('dispatch')

    def get_groups(self) -> list[TaskGroup]:
        return [group for group in set(self.pluck('group')) if group]
    
    def get_group_ids(self) -> list[TaskGroupId]:
        return self.pluck('group.id')
    
    @staticmethod
    def resolve_identifier(
        identifier: str | Task | TaskId | TaskAlias | TaskGroup | TaskGroupId | asyncio.Task,
    ) -> TaskId | TaskAlias | TaskGroupId:
        if isinstance(identifier, str):
            return TaskId(identifier)
        elif isinstance(identifier, Task):
            return  identifier.id
        elif isinstance(identifier, asyncio.Task):
            return  TaskId(identifier.get_name())
        elif isinstance(identifier, TaskGroup):
            return  TaskGroupId(identifier.id)
        
        return identifier
    
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