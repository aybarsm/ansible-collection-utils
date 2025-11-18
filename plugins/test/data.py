from __future__ import annotations
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Validate

class TestModule(object):
    def tests(self):
        return {
            'blank': Validate.blank,
            'filled': Validate.filled,
            'truthy': Validate.is_truthy,
            'falsy': Validate.is_falsy,
            'omitted': Validate.is_ansible_omitted,
            'type_name': Validate.is_type_name,
            'item_exec': Validate.is_item_exec,
            'mapping': Validate.is_mapping,
            'sequence': Validate.is_sequence,
        }