from __future__ import annotations
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Str

class FilterModule(object):
    def filters(self):        
        return {
            'str_before': Str.before,
            'str_before_last': Str.before_last,
            'str_after': Str.after,
            'str_after_last': Str.after_last,
            'str_matches': Str.matches,
            'str_finish': Str.finish,
            'str_start': Str.start,
            'str_wrap': Str.wrap,
            'str_quote': Str.quote,
            'str_strip': lambda data, chars = None: str(data).strip(chars),
            'str_lstrip': lambda data, chars = None: str(data).lstrip(chars),
            'str_rstrip': lambda data, chars = None: str(data).rstrip(chars),
            'str_remove_empty_lines': Str.remove_empty_lines,
        }