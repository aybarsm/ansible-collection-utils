### BEGIN: Imports
import typing as t
import typing_extensions as te
import dataclasses as dt
import enum, functools, uuid, datetime, hashlib
### END: Imports
### BEGIN: ImportManager
### END: ImportManager

### BEGIN: Data Classes
dataclass = dt.dataclass

@functools.wraps(dt.dataclass)
def model_class(cls=None, /, **kwargs):
    kwargs['init']=True
    kwargs['kw_only']=True
    return dt.dataclass(cls, **kwargs)

@functools.wraps(dt.field)
def model_field(**kwargs):
    options = Data_all_except(kwargs, *CONF_['data_classes']['kwargs'].keys())
    kwargs = Data_only_with(kwargs, *CONF_['data_classes']['kwargs'].keys())
    kwargs = Data_combine(kwargs, {'metadata': {'_options': options}}, recursive=True)
    return dt.field(**kwargs)

def model_method(**kwargs):
    def decorator(func):        
        setattr(func, '__metadata__', kwargs)
        return func
    return decorator
### END: Data Classes

### BEGIN: Generic - Definitions
@dataclass(frozen=True, kw_only=True)
class _Sentinel:
    raw: object = model_field(init=True)
    ts: datetime.datetime = model_field(init=True)
    ts_str: str = model_field(init=True)
    ts_safe: str = model_field(init=True)
    id: str = model_field(init=True)
    hash: str = model_field(init=True)

    @staticmethod
    def make() -> "_Sentinel":
        raw_ = object()
        ts_ = datetime.datetime.now(datetime.timezone.utc)
        ts_str_ = str(ts_.strftime('%Y-%m-%dT%H:%M:%SZ'))
        ts_safe_ = str(ts_.strftime('%Y%m%dT%H%M%SZ'))
        id_ = f'{str(id(raw_))}_{str(ts_.strftime('%Y-%m-%dT%H:%M:%S'))}.{ts_.microsecond * 1000:09d}Z'
        hash_ = hashlib.md5(id_.encode()).hexdigest()
        return _Sentinel(raw=raw_, ts=ts_, ts_str=ts_str_, ts_safe=ts_safe_, id=id_, hash=hash_)

@dataclass(frozen=True)
class Separator:
    char: str = model_field(default='-', init=True)
    times: PositiveInt = model_field(default=50, init=True)

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

@dataclass(kw_only=True)
class BaseModel:
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
            # Utils_dump(Convert_as_callable_caller_segments(self, '__getattribute__'))
            raise RuntimeError(f'Protected method [{name}] cannot be called externally.')
        elif is_hidden_field and not Validate_callable_called_within_hierarchy(self, '__getattribute__'):
            raise RuntimeError(f'Hidden attribute [{name}] cannot be accessed externally.')

        return attr
### END: Generic - Definitions

### BEGIN: Models
@dataclass(init=True, frozen=True, kw_only=True)
class CommandModel:
    rc: t.Optional[int] = model_field(default=None, init=True)
    out: t.Optional[str] = model_field(default=None, init=True)
    err: t.Optional[str] = model_field(default=None, init=True)
    command: t.Optional[str] = model_field(default=None, init=True)

    @property
    def output(self) -> t.Optional[str]:
        return self.out
    
    @property
    def error(self) -> t.Optional[str]:
        return self.err
    
    def lines(self, cleaned: bool = False) -> list[str]:
        return self.output_lines(cleaned) + self.error_lines(cleaned)
    
    def output_lines(self, cleaned: bool = False) -> list[str]:
        return Convert_as_cleaned_lines(self.out) if cleaned else Convert_as_lines(self.out)

    def error_lines(self, cleaned: bool = False) -> list[str]:
        return Convert_as_cleaned_lines(self.err) if cleaned else Convert_as_lines(self.err)
    
    @property
    def has_rc(self) -> bool:
        return Validate_filled(self.rc)
    
    @property
    def has_output(self) -> bool:
        return Validate_filled(self.out)
    
    @property
    def has_error(self) -> bool:
        return Validate_filled(self.err)
    
    @property
    def has_command(self) -> bool:
        return Validate_filled(self.command)

    @property
    def success(self) -> bool:
        return self.rc == 0
    
    @property
    def failed(self) -> bool:
        return not self.success
    
    # def is_(self, src: t.Literal['output', 'error'], of: t.Literal['json', 'yaml', 'lua', 'toml']) -> bool:
    #     rel = self.output if src == 'output' else self.err
        
    #     if not rel or Validate_blank(rel):
    #         return False
    

### END: Models

### BEGIN: Events
@dataclass(kw_only=True, frozen=True)
class StatusChangedEvent:
    related: t.Any
    previous: GenericStatus
    current: GenericStatus
### END: Events

### BEGIN: Mixins
@dataclass(kw_only=True)
class IdMixin:
    id: UniqueIdUuid = model_field(default_factory=uuid.uuid4, init=False, repr=True, frozen=True)
    alias: t.Optional[UniqueAlias] = model_field(default=None, init=True, repr=True, frozen=True)

@dataclass(kw_only=True)
class CallableMixin:
    @model_method(protected=True)
    def _caller_get_config(self, *args, **kwargs):
        args = list(args or [])
        kwargs = dict(kwargs or {})

        kwargs = Data_append(kwargs, '__caller.bind.annotations', self)

        if 'context' not in kwargs:
            ph = Factory_placeholder()
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
    
    @model_method(protected=True)
    def _caller_make_call(self, callback: t.Optional[t.Callable], *args, **kwargs) -> t.Any:
        if not callback:
            return

        args, kwargs = self._caller_get_config(*args, **kwargs)
        
        return Utils_call(callback, *args, **kwargs)

@dataclass(kw_only=True)
class StatusMixin:
    status: GenericStatus = model_field(default=GenericStatus.READY, init=False, repr=True, protected=True)
    on_status_change: t.Optional[EventCallback] = model_field(default=None, init=True, repr=True, frozen=True)
    
    @model_method(protected=True)
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
### END: Singletons