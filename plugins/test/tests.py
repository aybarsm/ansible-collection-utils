from __future__ import annotations
from ansible_collections.aybarsm.utils.plugins.module_utils.aggregator import Aggregator

Validate = Aggregator.tools.validate

class TestModule(object):
    def tests(self):
        return {
            'blank': Validate.blank,
            'filled': Validate.filled,
            'path_exists': Validate.path_exists,
            'file_exists': Validate.file_exists,
            'dir_exists': Validate.dir_exists,
            'filled_type': lambda data, type: Validate.filled(data) and Validate.is_type_of(data, type),
            'str_starts': lambda data, needle: str(data).startswith(needle),
            'str_ends': lambda data, needle: str(data).endswith(needle),
            'str_contains': lambda data, needle: str(needle) in str(data),
            'str_regex': Validate.str_is_regex,
            'str_match': Validate.str_is_match,
            'omitted': Validate.is_omitted,
            'type_name': Validate.is_type_name,
            'truthy': Validate.is_truthy,
            'falsy': Validate.is_falsy,
        }