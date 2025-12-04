# BEGIN: Imports
from __future__ import annotations
from jinja2 import pass_context
# END: Imports
# BEGIN: ImportManager
# END: ImportManager

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
            'data_unique_by': Data_unique_by,
            'data_keys': Data_keys,
            'data_where': Data_where,
            'data_to_dot': Data_dot,
        }