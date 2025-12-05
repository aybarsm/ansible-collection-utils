### BEGIN: Imports
from __future__ import annotations
### END: Imports
### BEGIN: ImportManager
### END: ImportManager

class TestModule(object):
    def tests(self):
        return {
            'fs_path_exists': Validate_fs_path_exists,
            'fs_file_exists': Validate_fs_file_exists,
            'fs_dir_exists': Validate_fs_dir_exists,
        }