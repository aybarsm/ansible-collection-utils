### BEGIN: Imports
from __future__ import annotations
from jinja2 import pass_context
from ansible_collections.aybarsm.utils.plugins.module_utils import DataQueryExecutor
### END: Imports
### BEGIN: ImportManager
from ansible_collections.aybarsm.utils.plugins.module_utils.support.data import (
	Data_all_except, Data_combine, Data_combine_match,
	Data_dot, Data_get, Data_keys,
	Data_only_with, Data_pluck, Data_uniq,
	Data_where,
)
### END: ImportManager

@pass_context
def data_query(context, data, query, *bindings, **kwargs):
    return DataQueryExecutor(context, data, query, *bindings, **kwargs).execute()

class FilterModule(object):
    def filters(self):
        return {
            'data_query': data_query,
            'data_only_with': Data_only_with,
            'data_all_except': Data_all_except,
            'data_combine_match': Data_combine_match,
            'data_combine': Data_combine,
            'data_get': Data_get,
            'data_pluck': Data_pluck,
            'data_unique': Data_uniq,
            'data_keys': Data_keys,
            'data_where': Data_where,
            'data_to_dot': Data_dot,
        }