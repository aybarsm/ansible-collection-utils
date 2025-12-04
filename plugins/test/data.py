from __future__ import annotations
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Validate

class TestModule(object):
    def tests(self):
        return {
            'blank': Kit.Validate().blank,
            'filled': Kit.Validate().filled,
            'truthy': Kit.Validate().is_truthy,
            'falsy': Kit.Validate().is_falsy,
            'omitted': Kit.Validate().is_ansible_omitted,
            'type_name': Kit.Validate().is_type_name,
            'item_exec': Kit.Validate().is_item_exec,
            'mapping': Kit.Validate().is_mapping,
            'sequence': Kit.Validate().is_sequence,
        }