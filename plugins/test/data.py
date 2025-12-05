### BEGIN: Imports
from __future__ import annotations
### END: Imports
### BEGIN: ImportManager
### END: ImportManager

class TestModule(object):
    def tests(self):
        return {
            'blank': Validate_blank,
            'filled': Validate_filled,
            'truthy': Validate_is_truthy,
            'falsy': Validate_is_falsy,
            'omitted': Validate_is_ansible_omitted,
            'type_name': Validate_is_type_name,
            'item_exec': Validate_is_item_exec,
            'mapping': Validate_is_mapping,
            'sequence': Validate_is_sequence,
        }