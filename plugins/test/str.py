# BEGIN: Imports
from __future__ import annotations
# END: Imports
# BEGIN: ImportManager
# END: ImportManager

class TestModule(object):
    def tests(self):
        return {
            'str_starts': Validate_str_starts,
            'str_ends': Validate_str_ends,
            'str_contains': Validate_str_contains,
            'str_matches': Validate_str_matches,
        }