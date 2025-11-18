from __future__ import annotations
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers import Convert

class FilterModule(object):
    def filters(self):        
        return {
            'to_querystring': Convert.to_querystring,
            'to_iterable': Convert.to_iterable,
            'to_safe_json': Convert.to_safe_json,
            'to_lofs': Convert.to_list_of_dicts,
            'to_type_name': Convert.to_type_name,
            'to_native': Convert.to_text,
            'to_string': Convert.to_string,
            'to_hash_scrypt': Convert.to_hash_scrypt,
            'to_ts_mod': Convert.as_ts_mod,
            'from_cli': Convert.from_cli,
            'from_lua':Convert.from_lua,
            'to_lua':Convert.to_lua,
            'from_toml':Convert.from_toml,
            'to_toml':Convert.to_toml,
            'as_ip_address': Convert.as_ip_address,
            'as_ip_segments': Convert.as_ip_segments,
        }