from __future__ import annotations
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Validate

class TestModule(object):
    def tests(self):
        return {
            'fs_path_exists': Validate.fs_path_exists,
            'fs_file_exists': Validate.fs_file_exists,
            'fs_dir_exists': Validate.fs_dir_exists,
        }