from __future__ import annotations
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Validate

class TestModule(object):
    def tests(self):
        return {
            'str_starts': lambda data, needle: str(data).startswith(needle),
            'str_ends': lambda data, needle: str(data).endswith(needle),
            'str_contains': Validate.str_contains,
            'str_matches': Validate.str_matches,
        }