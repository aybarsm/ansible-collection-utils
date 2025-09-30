from __future__ import annotations
from ansible_collections.aybarsm.utils.plugins.module_utils.aggregator import Aggregator

Data = Aggregator.tools.data
Str = Aggregator.tools.str
Helper = Aggregator.tools.helper

class FilterModule(object):
    def filters(self):        
        return {
            'only_with': Data.only_with,
            'all_except': Data.all_except,
            'combine_match': Data.combine_match,
            'combine': Data.combine,
            'dq': Data.query,
            'dg': Data.get,
            'data_get': Data.get,
            'to_querystring': Helper.to_querystring,
            'to_iterable': Helper.to_iterable,
            'to_safe_json': Helper.to_safe_json,
            'to_lofs': Helper.to_list_dicts,
            'top_level_dirs': Helper.top_level_dirs,
            'str_cli': Str.to_cli,
            'str_tokenize': Str.to_tokens,
            'str_wrap': Str.wrap,
        }