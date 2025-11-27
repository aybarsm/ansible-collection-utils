import typing as t
import types as tt
import dataclasses as dt
import typing_extensions as te
import pydantic as tp
import inspect
import enum

# BEGIN: Generic - Definitions
class CommonStatus(enum.Enum):
    QUEUED = enum.auto()
    NOT_EXECUTED = enum.auto()
    RUNNING = enum.auto()
    FINISHED = enum.auto()
    FAILED = enum.auto()
    ABORTED = enum.auto()
    CANCELLED = enum.auto()
    SKIPPED = enum.auto()

def immutable_data(cls):
    return dt.dataclass(frozen=True)(cls)
# END: Generic - Definitions

# BEGIN: Generic - Types
SENTINEL = object()
T = t.TypeVar("T")
ENUMERATABLE = t.Union[list[T], tuple[T, ...], set[T]]

MappingImmutable = tt.MappingProxyType
# END: Generic - Types

# BEGIN: Pydantic - Types
PositiveInt = tp.PositiveInt
PositiveFloat = tp.PositiveFloat
# BEGIN: End - Types

# BEGIN: Task

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

@immutable_data
class CallableSegmentParameter:
    pos: int
    type_: CallableParameterKind
    name: str
    annotation: type
    default: t.Any
    item: inspect.Parameter
    kind: inspect._ParameterKind
    
    @immutable_data
    class has:
        default: bool
        annotation: bool

@immutable_data
class CallableSegments:
    name: t.Optional[str]
    params: tuple[CallableSegmentParameter]

    @immutable_data
    class is_:
        named: bool = False
        anonymous: bool = False
    
    @immutable_data
    class has:
        @immutable_data
        class params:
            pos: bool = False
            key: bool = False
            any: bool = False
            args: bool = False
            kwargs: bool = False
            empty: bool = False
# END: Callable