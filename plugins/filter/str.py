from __future__ import annotations
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Str

class FilterModule(object):
    def filters(self):        
        return {
            'str_before': Kit.Str().before,
            'str_before_last': Kit.Str().before_last,
            'str_after': Kit.Str().after,
            'str_after_last': Kit.Str().after_last,
            'str_matches': Kit.Str().matches,
            'str_finish': Kit.Str().finish,
            'str_start': Kit.Str().start,
            'str_wrap': Kit.Str().wrap,
            'str_quote': Kit.Str().quote,
            'str_strip': lambda data, chars = None: str(data).strip(chars),
            'str_lstrip': lambda data, chars = None: str(data).lstrip(chars),
            'str_rstrip': lambda data, chars = None: str(data).rstrip(chars),
            'str_remove_empty_lines': Kit.Str().remove_empty_lines,
        }