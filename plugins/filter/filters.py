from __future__ import annotations
from ansible_collections.aybarsm.utils.plugins.module_utils.tools import Data, Str, Helper

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
            'str_finish': Str.finish,
            'str_start': Str.start,
            'ip_as_addr': Helper.ip_as_addr,
            'subnets_collapse': Helper.subnets_collapse,
            'type_name': Helper.to_type_name,
            'to_native': Helper.to_native,
            'to_string': Helper.to_string,
            'to_lua': Helper.to_lua,
            'ts_mod': Helper.ts_mod,
            'path_tmp': Helper.path_tmp,
        }