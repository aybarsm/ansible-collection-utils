import typing as t

# BEGIN: Generic
SENTINEL = object()
T = t.TypeVar("T")
ENUMERATABLE = t.Union[list[T], tuple[T, ...], set[T]]
# END: Generic

# BEGIN: Task
TaskId = str
TaskAlias = t.Optional[str]
TaskGroup = t.Optional[str]
TaskResult = t.Any
TaskCallback = t.Callable[..., TaskResult]
TaskOnFinallyCallback = t.Optional[t.Callable[..., None]]

TaskChannelSize = int
# END: Task

# BEGIN: Callable
CallableParameterKind = t.Literal[
    'positional_or_keyword', 
    'positional', 
    'positional_only', 
    'keyword', 
    'keyword_only', 
    'empty',
]
# END: Callable