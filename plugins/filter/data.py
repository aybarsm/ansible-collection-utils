from __future__ import annotations
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Data

class FilterModule(object):
    def filters(self):        
        return {
            'data_only_with': Data.only_with,
            'data_all_except': Data.all_except,
            'data_combine_match': Data.combine_match,
            'data_combine': Data.combine,
            'data_get': Data.get,
            'data_pluck': Data.pluck,
            'data_unique_by': Data.unique_by,
            'data_keys': Data.keys,
            'data_where': Data.where,
            'data_to_dot': Data.dot,
        }