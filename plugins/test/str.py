from __future__ import annotations
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Validate

class TestModule(object):
    def tests(self):
        return {
            'str_starts': Kit.Validate().str_starts,
            'str_ends': Kit.Validate().str_ends,
            'str_contains': Kit.Validate().str_contains,
            'str_matches': Kit.Validate().str_matches,
        }