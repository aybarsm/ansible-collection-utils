# BEGIN: Imports
from __future__ import annotations
# END: Imports
# BEGIN: ImportManager
# END: ImportManager

class FilterModule(object):
    def filters(self):
        return {
            'to_querystring': Convert_to_querystring,
            'to_iterable': Convert_to_iterable,
            'to_safe_json': Convert_to_safe_json,
            'to_lofs': Convert_to_list_of_dicts,
            'to_type_name': Convert_to_type_name,
            'to_native': Convert_to_text,
            'to_string': Convert_to_string,
            'to_hash_scrypt': Convert_to_hash_scrypt,
            'to_ts_mod': Convert_as_ts_mod,
            'from_cli': Convert_from_cli,
            'from_lua':Convert_from_lua,
            'to_lua':Convert_to_lua,
            'from_toml':Convert_from_toml,
            'to_toml':Convert_to_toml,
            'as_ip_address': Convert_as_ip_address,
            'as_ip_segments': Convert_as_ip_segments,
        }