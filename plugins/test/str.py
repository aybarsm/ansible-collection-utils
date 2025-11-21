from __future__ import annotations
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Validate

class TestModule(object):
    def tests(self):
        return {
            'str_starts': Validate.str_starts,
            'str_ends': Validate.str_ends,
            'str_contains': Validate.str_contains,
            'str_matches': Validate.str_matches,
        }