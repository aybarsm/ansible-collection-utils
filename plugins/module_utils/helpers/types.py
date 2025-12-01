import typing as t
import types as tt
import typing_extensions as te
import pydantic as tp
import inspect, datetime, hashlib, uuid

# BEGIN: Generic - Types
T = t.TypeVar("T")
ENUMERATABLE = t.Union[list[T], tuple[T, ...], set[T]]

SENTINEL: object = object()
SENTINEL_TS: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)
SENTINEL_ID: str = f'{str(id(SENTINEL))}_{str(SENTINEL_TS.strftime('%Y-%m-%dT%H:%M:%S'))}.{SENTINEL_TS.microsecond * 1000:09d}Z'
SENTINEL_HASH: str = hashlib.md5(SENTINEL_ID.encode()).hexdigest()

MappingImmutable = tt.MappingProxyType
EventCallback = t.Callable[..., None]
UniqueIdInt = tp.PositiveInt
UniqueIdStr = str
UniqueIdUuid = uuid.UUID
UniqueAlias = str
# END: Generic - Types

# BEGIN: Pydantic - Types
PydanticBaseModel = tp.BaseModel
PositiveInt = tp.PositiveInt
PositiveFloat = tp.PositiveFloat
# BEGIN: End - Types

# BEGIN: Task
TaskResult = t.Any
TaskCallback = t.Callable[..., TaskResult]
TaskGroupConcurrent = PositiveInt
# END: Task

# BEGIN: Callable
CallableParameterKindMap = tt.MappingProxyType({
    'any': inspect.Parameter.POSITIONAL_OR_KEYWORD,
    'pos': inspect.Parameter.POSITIONAL_ONLY,
    'key': inspect.Parameter.KEYWORD_ONLY,
    'empty': inspect.Parameter.empty,
    'args': inspect.Parameter.VAR_POSITIONAL,
    'kwargs': inspect._ParameterKind.VAR_KEYWORD,
})

CallableParameterTypeMap = tt.MappingProxyType({v: k for k, v in CallableParameterKindMap.items()})

CallableParameterKind = t.Literal['any', 'pos', 'key', 'empty', 'args', 'kwargs']
CallableParameterHas = t.Literal['default', 'annotation']