import typing as t
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Convert, Factory
from ansible_collections.aybarsm.utils.plugins.module_utils.tools.fluent import Fluent
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.types import (
    immutable_data
)

@immutable_data
class DataIdFactory:
    prefix: str = Factory.random_string(16)
    suffix: str = Factory.random_string(16)
    ts: str = str(Factory.ts(mod='long'))
    data: Fluent = Fluent()

    def make(self, data: t.Any) -> str:
        return Convert.as_id(
            data=data, 
            prefix=f'{self.prefix}_', 
            suffix=f'_{self.ts}_{self.suffix}',
            use_ts=False,
        )