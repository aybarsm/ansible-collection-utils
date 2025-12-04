# BEGIN: Imports
from __future__ import annotations
# END: Imports
# BEGIN: ImportManager
# END: ImportManager

class FilterModule(object):
    def filters(self):
        from ansible_collections.aybarsm.utils.plugins.module_utils.aggregator import Kit
        return {
            'str_before': Str_before,
            'str_before_last': Str_before_last,
            'str_after': Str_after,
            'str_after_last': Str_after_last,
            'str_matches': Str_matches,
            'str_finish': Str_finish,
            'str_start': Str_start,
            'str_wrap': Str_wrap,
            'str_quote': Str_quote,
            'str_strip': lambda data, chars = None: str(data).strip(chars),
            'str_lstrip': lambda data, chars = None: str(data).lstrip(chars),
            'str_rstrip': lambda data, chars = None: str(data).rstrip(chars),
            'str_remove_empty_lines': Str_remove_empty_lines,
        }