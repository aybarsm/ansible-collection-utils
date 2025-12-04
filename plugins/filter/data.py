from __future__ import annotations
from jinja2 import pass_context
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.data_query_executor import DataQueryExecutor

@pass_context
def data_query(context, data, query, *bindings, **kwargs):
    return DataQueryExecutor(context, data, query, *bindings, **kwargs).execute()

class FilterModule(object):
    def filters(self):
        from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Data
        
        return {
            'data_query': data_query,
            'data_only_with': Kit.Data().only_with,
            'data_all_except': Kit.Data().all_except,
            'data_combine_match': Kit.Data().combine_match,
            'data_combine': Kit.Data().combine,
            'data_get': Kit.Data().get,
            'data_pluck': Kit.Data().pluck,
            'data_unique_by': Kit.Data().unique_by,
            'data_keys': Kit.Data().keys,
            'data_where': Kit.Data().where,
            'data_to_dot': Kit.Data().dot,
        }