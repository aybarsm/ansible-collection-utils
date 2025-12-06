### BEGIN: Imports
import typing as t
import types as tt
import typing_extensions as te
import annotated_types as at
import dataclasses as dt
import enum, functools, uuid, datetime, hashlib, inspect, re, uuid
### END: Imports
### BEGIN: ImportManager
from ansible_collections.aybarsm.utils.plugins.module_utils.support.data import (
	Data_all_except, Data_append, Data_combine,
	Data_get, Data_only_with,
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.utils import (
	Utils_call, 
)
from ansible_collections.aybarsm.utils.plugins.module_utils.support.validate import (
	Validate_callable_called_within_hierarchy, Validate_filled,
	Validate_is_callable,
)
### END: ImportManager

## BEGIN: Generic - Types
T = t.TypeVar("T")
ENUMERATABLE = t.Union[list[T], tuple[T, ...], set[T]]

MappingImmutable = tt.MappingProxyType
EventCallback = t.Callable[..., None]

PositiveInt = t.Annotated[int, at.Gt(0)]
NegativeInt = t.Annotated[int, at.Lt(0)]
NonPositiveInt = t.Annotated[int, at.Le(0)]
NonNegativeInt = t.Annotated[int, at.Ge(0)]

PositiveFloat = t.Annotated[float, at.Gt(0)]
NegativeFloat = t.Annotated[float, at.Lt(0)]
NonPositiveFloat = t.Annotated[float, at.Le(0)]
NonNegativeFloat = t.Annotated[float, at.Ge(0)]

UniqueIdInt = PositiveInt
UniqueIdStr = str
UniqueIdUuid = uuid.UUID
UniqueAlias = str
### END: Generic - Types

### BEGIN: Modules
def cerberus():
    import cerberus
    return cerberus

def pydantic():
    import pydantic
    return pydantic

def pydash():
    import pydash
    return pydash
### END: Modules

### BEGIN: Data Classes
@functools.wraps(dt.dataclass)
def model(
    cls=None, /, *, 
    init=True, repr=True, eq=True, order=False, 
    unsafe_hash=False, frozen=False, match_args=True, 
    kw_only=False, slots=False, weakref_slot=False, 
    **kwargs
):
    params = locals()
    del params['cls']
    
    if cls:
        setattr(cls, '__metadata__', params.pop('kwargs', {}))
    else:
        del params['kwargs']

    return dt.dataclass(cls, **params)
   
@functools.wraps(dt.field)
def field(
    *, 
    default=dt.MISSING, default_factory=dt.MISSING, init=True, 
    repr=True, hash=None, compare=True, metadata=None, 
    kw_only=dt.MISSING, 
    **kwargs
):
    params = locals()

    if params['metadata'] == None:
        params['metadata'] = {}

    if Validate_filled(params.get('kwargs', {})):
        params['metadata'] = Data_combine(params['metadata'], {'_options': params.pop('kwargs', {})}, recursive=True)

    if params['metadata'].get('hidden', False) == True:
        params['repr'] = False

    return dt.field(**params)

@functools.wraps(dt.make_dataclass)
def make_model(
    cls_name, fields, *, bases=(), namespace=None, init=True,
    repr=True, eq=True, order=False, unsafe_hash=False,
    frozen=False, match_args=True, kw_only=False, slots=False,
    weakref_slot=False, module=None,
    **kwargs
) -> "Model":
    params = locals()
    del params['cls_name']
    del params['fields']
    
    params['bases'] = [base for base in list(params['bases']) if base != Model]
    params['bases'].insert(0, Model)
    params['bases'] = tuple(params['bases'])

    # metadata = params.pop('kwargs', {})

    return dt.make_dataclass(cls_name, fields, **params)

def method(**kwargs):
    def decorator(func):        
        setattr(func, '__metadata__', kwargs)
        return func
    return decorator
### END: Data Classes

### BEGIN: Generic - Definitions
@dt.dataclass(frozen=True, kw_only=True)
class _Sentinel:
    raw: object = field(init=True)
    ts: datetime.datetime = field(init=True)
    ts_str: str = field(init=True)
    ts_safe: str = field(init=True)
    id: str = field(init=True)
    hash: str = field(init=True)

    @staticmethod
    def make() -> "_Sentinel":
        raw_ = object()
        ts_ = datetime.datetime.now(datetime.timezone.utc)
        ts_str_ = str(ts_.strftime('%Y-%m-%dT%H:%M:%SZ'))
        ts_safe_ = str(ts_.strftime('%Y%m%dT%H%M%SZ'))
        id_ = f'{str(id(raw_))}_{str(ts_.strftime('%Y-%m-%dT%H:%M:%S'))}.{ts_.microsecond * 1000:09d}Z'
        hash_ = hashlib.md5(id_.encode()).hexdigest()
        return _Sentinel(raw=raw_, ts=ts_, ts_str=ts_str_, ts_safe=ts_safe_, id=id_, hash=hash_)

@dt.dataclass(frozen=True)
class Separator:
    char: str = field(default='-', init=True)
    times: PositiveInt = field(default=50, init=True)

    def make(self) -> str:
        return self.char * self.times

class GenericStatus(enum.StrEnum):
    ABORTED = enum.auto()
    CANCELLED = enum.auto()
    COMPLETED = enum.auto()
    FAILED = enum.auto()
    QUEUED = enum.auto()
    READY = enum.auto()
    RUNNING = enum.auto()
    SKIPPED = enum.auto()
    TIMED_OUT = enum.auto()

    def is_(self, *of: "GenericStatus") -> bool:
        return self in of
    
    def not_(self, *of: "GenericStatus") -> bool:
        return self not in of

    def aborted(self) -> bool:
        return self.is_(self.ABORTED)
    
    def cancelled(self) -> bool:
        return self.is_(self.CANCELLED)
    
    def canceled(self) -> bool:
        return self.cancelled()
    
    def completed(self) -> bool:
        return self.is_(self.COMPLETED)
    
    def failed(self) -> bool:
        return self.is_(self.FAILED)

    def queued(self) -> bool:
        return self.is_(self.QUEUED)
    
    def ready(self) -> bool:
        return self.is_(self.READY)
    
    def running(self) -> bool:
        return self.is_(self.RUNNING)
    
    def skipped(self) -> bool:
        return self.is_(self.SKIPPED)
    
    def timed_out(self) -> bool:
        return self.is_(self.TIMED_OUT)
    
    def abortable(self) -> bool:
        return self.running()
    
    def dispatchable(self) -> bool:
        return self.is_(self.READY, self.QUEUED)
    
    def dispatched(self) -> bool:
        return self.not_(self.READY, self.QUEUED)
    
    def finished(self) -> bool:
        return self.not_(self.READY, self.QUEUED, self.RUNNING)
    
    def cancellable(self) -> bool:
        return self.is_(self.READY, self.QUEUED)
    
    def cancelable(self) -> bool:
        return self.cancelable()

@dt.dataclass(kw_only=True)
class Model:
    __metadata__: dict[str, t.Any] = field(default_factory=dict, init=False, protected=True, hidden=True)

    @staticmethod
    def make(*args, **kwargs):
        return make_model(*args, **kwargs)

    def __dataclass_field(self, name: str, key: str = '', default: t.Any = None) -> t.Any:
        attr = self.__dataclass_fields__.get(name)

        if attr is None:
            return default
        
        if key.strip() == '':
            return attr        

        return Data_get(attr, key, default)
        
    def __delattr__(self, name: str) -> None:
        if self.__dataclass_field(name, 'metadata._options.frozen') == True:
            raise RuntimeError(f'Frozen attribute [{name}] cannot be deleted.')
        
        is_protected = self.__dataclass_field(name, 'metadata._options.protected') == True
        if is_protected and not Validate_callable_called_within_hierarchy(self, '__delattr__'):
            raise RuntimeError(f'Protected attribute [{name}] cannot be deleted externally.')
        
        super().__delattr__(name)
    
    def __setattr__(self, name: str, value: t.Any) -> None:
        is_protected = self.__dataclass_field(name, 'metadata._options.protected') == True
        if is_protected and not Validate_callable_called_within_hierarchy(self, '__setattr__'):
            raise RuntimeError(f'Protected attribute [{name}] cannot be manipulated externally.')
        
        super().__setattr__(name, value)
    
    def __getattribute__(self, name: str) -> t.Any:
        attr = super().__getattribute__(name)
        
        if name in ['__class__', '__dataclass_fields__', '__dataclass_field']:
            return attr
        
        is_callable = Validate_is_callable(attr)
        is_protected_method = is_callable and Data_get(attr, '__metadata__.protected') == True
        is_hidden_field = not is_callable and self.__dataclass_field(name, 'metadata._options.hidden') == True

        if is_protected_method and not Validate_callable_called_within_hierarchy(self, '__getattribute__'):
            raise RuntimeError(f'Protected method [{name}] cannot be called externally.')
        elif is_hidden_field and not Validate_callable_called_within_hierarchy(self, '__getattribute__'):
            raise RuntimeError(f'Hidden attribute [{name}] cannot be accessed externally.')

        return attr
### END: Generic - Definitions

### BEGIN: Models
# @dt.dataclass(init=True, frozen=True, kw_only=True)
# class CommandModel:
#     rc: t.Optional[int] = field(default=None, init=True)
#     out: t.Optional[str] = field(default=None, init=True)
#     err: t.Optional[str] = field(default=None, init=True)
#     command: t.Optional[str] = field(default=None, init=True)

#     @property
#     def output(self) -> t.Optional[str]:
#         return self.out
    
#     @property
#     def error(self) -> t.Optional[str]:
#         return self.err
    
#     def lines(self, cleaned: bool = False) -> list[str]:
#         return self.output_lines(cleaned) + self.error_lines(cleaned)
    
#     def output_lines(self, cleaned: bool = False) -> list[str]:
#         return Convert_as_cleaned_lines(self.out) if cleaned else Convert_as_lines(self.out)

#     def error_lines(self, cleaned: bool = False) -> list[str]:
#         return Convert_as_cleaned_lines(self.err) if cleaned else Convert_as_lines(self.err)
    
#     @property
#     def has_rc(self) -> bool:
#         return Validate_filled(self.rc)
    
#     @property
#     def has_output(self) -> bool:
#         return Validate_filled(self.out)
    
#     @property
#     def has_error(self) -> bool:
#         return Validate_filled(self.err)
    
#     @property
#     def has_command(self) -> bool:
#         return Validate_filled(self.command)

#     @property
#     def success(self) -> bool:
#         return self.rc == 0
    
#     @property
#     def failed(self) -> bool:
#         return not self.success
    
#     # def is_(self, src: t.Literal['output', 'error'], of: t.Literal['json', 'yaml', 'lua', 'toml']) -> bool:
#     #     rel = self.output if src == 'output' else self.err
        
#     #     if not rel or Validate_blank(rel):
#     #         return False
    

### END: Models

### BEGIN: Events
@dt.dataclass(kw_only=True, frozen=True)
class StatusChangedEvent:
    related: t.Any
    previous: GenericStatus
    current: GenericStatus
### END: Events

### BEGIN: Mixins
@dt.dataclass(kw_only=True)
class IdMixin:
    id: UniqueIdUuid = field(default_factory=uuid.uuid4, init=False, repr=True, frozen=True)
    alias: t.Optional[UniqueAlias] = field(default=None, init=True, repr=True, frozen=True)

@dt.dataclass(kw_only=True)
class CallableMixin:
    @method(protected=True)
    def _caller_get_config(self, *args, **kwargs):
        args = list(args or [])
        kwargs = dict(kwargs or {})

        kwargs = Data_append(kwargs, '__caller.bind.annotations', self)

        if 'context' not in kwargs:
            ph = Sentinel.hash
            context = ph
            try:
                context = getattr(self, 'context')
            except Exception:
                pass

            if context != ph:
                if context not in args:
                    args.append(context)
                
                is_in_map_annotations = type(context) in Data_get(kwargs, '__caller.bind.annotation', {})
                is_in_iter_annoations = type(context) in Data_get(kwargs, '__caller.bind.annotations', [])
                if not is_in_map_annotations and not is_in_iter_annoations:
                    Data_append(kwargs, '__caller.bind.annotations', context)
        
        return [args, kwargs]
    
    @method(protected=True)
    def _caller_make_call(self, callback: t.Optional[t.Callable], *args, **kwargs) -> t.Any:
        if not callback:
            return

        args, kwargs = self._caller_get_config(*args, **kwargs)
        
        return Utils_call(callback, *args, **kwargs)

@dt.dataclass(kw_only=True)
class StatusMixin:
    status: GenericStatus = field(default=GenericStatus.READY, init=False, repr=True, protected=True)
    on_status_change: t.Optional[EventCallback] = field(default=None, init=True, repr=True, frozen=True)
    
    @method(protected=True)
    def _set_status(self, status: GenericStatus) -> te.Self:
        if self.status == status:
            return self
        
        previous = self.status
        self.status = status

        if not self.on_status_change:
            return self
        
        kwargs = {
            '__caller': {
                'bind': {
                    'annotations': [
                        StatusChangedEvent(related=self, previous=previous, current=status),
                    ],
                },
            },
        }

        Utils_call(self.on_status_change, **kwargs)

        return self
### END: Mixins

### BEGIN: Singletons
Sentinel = _Sentinel.make()

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

CONF = tt.MappingProxyType(
    {
        'data_classes': {
            'kwargs': {
                'default': dt.MISSING,
                'default_factory': dt.MISSING,
                'init': True,
                'repr': True,
                'hash': None,
                'compare': True,
                'metadata': None, 
                'kw_only': dt.MISSING,
            },
        },
        'pydantic': {
            'extras': {
                'protected': False,
            },
        },
        'data_query': {
            'defaults': {
                'bindings': {
                    'named': {
                        '_true': True,
                        '_false': False,
                    },
                },
            },
            'test': {
                'prefixes': {
                    'a.b.': "ansible.builtin.",
                    'a.u.': "ansible.utils.",
                    'c.g.': "community.general.",
                    'ayb.a.': 'aybarsm.all.',
                    'ayb.u.': 'aybarsm.utils.',
                },
            },
        },
        'jinja': {
            "prefixes": {
                "a.b.": "ansible.builtin.",
                "a.u.": "ansible.utils.",
                "c.g.": "community.general.",
                "ayb.a.": "aybarsm.all.",
                "ayb.u.": "aybarsm.utils.",
            },
        },
        'validate': {
            "ansible": {
                "entrypoints":
                    [
                        "ansible.cli.adhoc",
                        "ansible_builder.cli",
                        "ansible_collections.ansible_community",
                        "ansible.cli.config",
                        "ansible.cli.console",
                        "ansible.cli.doc",
                        "ansible.cli.galaxy",
                        "ansible.cli.inventory",
                        "ansiblelint.__main__",
                        "ansible.cli.playbook",
                        "ansible.cli.pull",
                        "ansible_test._util.target.cli.ansible_test_cli_stub",
                        "ansible.cli.vault",
                    ]
            },
        },
        'validator': {
            'regex': {
                'ipv4': re.compile(r'^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:\/[1-9]|\/[0-2]\d|\/3[0-2])?$'),
                'ipv4_address': re.compile(r'^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}$'),
                'ipv4_subnet': re.compile(r'^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}\/(?:[1-9]|[0-2]\d|3[0-2])$'),
                'ipv6': re.compile(r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))(?:\/[1-9]|\/[1-9][1-9]|\/1[0-2][0-8])?$'),
                'ipv6_address': re.compile(r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$'),
                'ipv6_subnet': re.compile(r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))\/(?:[1-9]|[1-9][1-9]|1[0-2][0-8])$'),
                'mac_address': re.compile(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'),
                'md5': re.compile(r'^[0-9a-f]{32}$'),
            }
        },
    }
)
### END: Singletons