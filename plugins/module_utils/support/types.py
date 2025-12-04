import typing as t
import types as tt
import typing_extensions as te
import annotated_types
import inspect, uuid

# BEGIN: Generic - Types
T = t.TypeVar("T")
ENUMERATABLE = t.Union[list[T], tuple[T, ...], set[T]]

MappingImmutable = tt.MappingProxyType
EventCallback = t.Callable[..., None]

PositiveInt = t.Annotated[int, annotated_types.Gt(0)]
NegativeInt = t.Annotated[int, annotated_types.Lt(0)]
NonPositiveInt = t.Annotated[int, annotated_types.Le(0)]
NonNegativeInt = t.Annotated[int, annotated_types.Ge(0)]

PositiveFloat = t.Annotated[float, annotated_types.Gt(0)]
NegativeFloat = t.Annotated[float, annotated_types.Lt(0)]
NonPositiveFloat = t.Annotated[float, annotated_types.Le(0)]
NonNegativeFloat = t.Annotated[float, annotated_types.Ge(0)]

UniqueIdInt = PositiveInt
UniqueIdStr = str
UniqueIdUuid = uuid.UUID
UniqueAlias = str
# END: Generic - Types


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