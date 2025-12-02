import typing as t
from pydantic import PositiveInt
import typing_extensions as te
import asyncio
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.types import (
    ENUMERATABLE, MappingImmutable, EventCallback, UniqueIdUuid, UniqueAlias, PositiveFloat,
    TaskResult, EventCallback, 
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.definitions import (
    dataclass, BaseModel, model_field, GenericStatus, IdMixin, StatusMixin
)
from ansible_collections.aybarsm.utils.plugins.module_utils.tools.task import Task, TaskGroup
from ansible_collections.aybarsm.utils.plugins.module_utils.tools.collection import Collection
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Convert, Data, Utils

TaskCollectionFindIdentifier = t.Union[UniqueIdUuid, UniqueAlias, Task, asyncio.Task]
TaskCollectionGetIdentifier = t.Union[TaskGroup, ENUMERATABLE[t.Union[UniqueIdUuid, UniqueAlias, Task, asyncio.Task, TaskGroup]]]
TaskCollectionIdentifier = t.Union[TaskCollectionFindIdentifier, TaskCollectionGetIdentifier]

@dataclass(init=False, kw_only=True)
class TaskCollection(Collection[Task], BaseModel):
    tasks: ENUMERATABLE[Task] = model_field(default_factory=list, init=True)
    context: t.Optional[t.Any] = model_field(default=None, init=True)

    def __init__(self,
        tasks: ENUMERATABLE[Task] = [],
        context: t.Optional[t.Any] = None,
    ):
        super().__init__(tasks)
        self.context: t.Optional[t.Any] = context
        
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
        identifier: TaskCollectionFindIdentifier,
    ) -> t.Optional[Task]:
        index = self.find_index(identifier)
        return None if index == None else self.items[index]
    
    def get(
        self,
        identifier: TaskCollectionGetIdentifier,
    ) -> tuple[Task, ...]:
        indexes = self.get_index(identifier)
        return tuple([self.items[index] for index in self.indexes() if index in indexes])
    
    def find_index(
        self,
        identifier: TaskCollectionFindIdentifier,
    ) -> t.Optional[int]:
        return self.first_index(self.resolve_retrieval_callback(identifier))
        
    def get_index(
        self,
        identifier: TaskCollectionGetIdentifier,
    ) -> tuple[int, ...]:
        return self.where_index(self.resolve_retrieval_callback(identifier))
    
    def get_ids(self) -> list[UniqueIdUuid]:
        return self.pluck('id')
    
    def get_aliases(self) -> list[UniqueAlias]:
        return self.pluck('alias')
    
    def get_results(self) -> list[TaskResult]:
        return self.pluck('result')
    
    def get_mapped_results(self) -> MappingImmutable[str, TaskResult]:
        return MappingImmutable(
            self.each(
                lambda task, idx, ret: Data.set_(ret, str(task.id), {'result': task.result, 'status': task.status}), 
                {}
            )
        )
    
    def get_dispatchers(self) -> list[t.Callable]:
        return self.pluck('dispatch')

    def get_groups(self) -> list[TaskGroup]:
        return self.pluck('group', filled=True, unique='id')
    
    def get_group_ids(self) -> list[UniqueIdUuid]:
        return self.pluck('group.id', filled=True, unique=True)
    
    def get_group_aliases(self) -> list[UniqueAlias]:
        return self.pluck('group.alias', filled=True, unique=True)
    
    @staticmethod
    def resolve_retrieval_callback(
        identifier: TaskCollectionIdentifier,
    ) -> t.Callable:
        done = set()
        callbacks = []

        for ident in Convert.to_iterable(identifier):
            if isinstance(ident, UniqueIdUuid):
                key, val = 'id', ident
            elif isinstance(ident, UniqueAlias):
                key, val = 'alias', ident
            elif isinstance(ident, Task):
                key, val = 'id', ident.id
            elif isinstance(ident, asyncio.Task):
                key, val = 'id', Convert.to_uuid(str(ident.get_name()))
            elif isinstance(ident, TaskGroup):
                key, val = 'group.id', ident.id
            
            key_done = f'{key}_{str(val)}'
            if key_done in done:
                continue

            callbacks.append(lambda task, key=key, val=val: Data.get(task, key) == val)
            done.add(key_done)
        
        return lambda task: any([cb(task) for cb in callbacks])
    
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

@dataclass(init=False, kw_only=True)
class TaskCollectionDispatchable(TaskCollection, IdMixin, StatusMixin):
    timeout: t.Optional[PositiveFloat] = model_field(default=None, init=True, kw_only=True)
    abort_on_failed: bool = model_field(default=True, init=True, kw_only=True)

    def __init__(
        self,
        tasks: ENUMERATABLE[Task] = [],
        context: t.Optional[t.Any] = None,
        timeout: t.Optional[PositiveFloat] = None,
        abort_on_failed: bool = True,
    ):
        super().__init__(tasks, context)
        
        self.timeout: t.Optional[PositiveFloat] = timeout
        self.abort_on_failed: bool = abort_on_failed
    
    def abort(self) -> te.Self:
        if not self.status.abortable():
            raise RuntimeError('Only running task collection can be aborted.')
        
        self._set_status(GenericStatus.ABORTED)

        return self