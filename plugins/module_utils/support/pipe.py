import typing as t
import typing_extensions as te
from ansible_collections.aybarsm.utils.plugins.module_utils.support.definitions import (
    dataclass, model_field, GenericStatus, BaseModel, IdMixin, StatusMixin, CallableMixin
)

AbortWhenCallback = t.Callable[..., bool]

@dataclass(init=True, kw_only=True)
class Pipe(BaseModel, IdMixin, StatusMixin, CallableMixin):
    context: t.Any = model_field(init=True, protected=True)
    abort_when: t.Optional[AbortWhenCallback] = model_field(default=None, init=True, frozen=True)
    last: t.Any = model_field(init=False, protected=True)
    
    def __call(self, callback: t.Callable, is_final: bool = False) -> te.Self:
        if self.status.aborted():
            return self
        
        if self.status.finished():
            raise RuntimeError('Pipe is already finished.')
        
        if self.status.dispatchable():
            self._set_status(GenericStatus.RUNNING)

        self.last = self._caller_make_call(callback)
        
        if not is_final and self.abort_when and self._caller_make_call(self.abort_when, self.last) == True:
            if self.status.abortable():
                self.abort()
            
            return self
        
        if not is_final and type(self.last) == type(self.context):
            self.context = self.last

        return self
    
    def next(self, callback: t.Callable) -> te.Self:
        return self.__call(callback)
    
    def then(self, callback: t.Callable) -> te.Self:
        if self.status.running():
            self._set_status(GenericStatus.COMPLETED)
        
        return self.__call(callback, False)

    def thenReturn(self) -> t.Any:
        if self.status.running():
            self._set_status(GenericStatus.COMPLETED)
        
        return self.context
    
    def thenLast(self) -> t.Any:
        if self.status.running():
            self._set_status(GenericStatus.COMPLETED)
        
        return self.last
    
    def abort(self) -> te.Self:
        if not self.status.abortable():
            raise RuntimeError('Only running pipe can be aborted.')
        
        self._set_status(GenericStatus.ABORTED)

        return self
    
    @staticmethod
    def send(context: t.Any, abort_when: t.Optional[AbortWhenCallback] = None) -> "Pipe":
        return Pipe(context=context, abort_when=abort_when)