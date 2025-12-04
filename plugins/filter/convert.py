from __future__ import annotations

class FilterModule(object):
    def filters(self):
        from ansible_collections.aybarsm.utils.plugins.module_utils.aggregator import Kit
        
        return {
            'to_querystring': Kit.Convert().to_querystring,
            'to_iterable': Kit.Convert().to_iterable,
            'to_safe_json': Kit.Convert().to_safe_json,
            'to_lofs': Kit.Convert().to_list_of_dicts,
            'to_type_name': Kit.Convert().to_type_name,
            'to_native': Kit.Convert().to_text,
            'to_string': Kit.Convert().to_string,
            'to_hash_scrypt': Kit.Convert().to_hash_scrypt,
            'to_ts_mod': Kit.Convert().as_ts_mod,
            'from_cli': Kit.Convert().from_cli,
            'from_lua':Kit.Convert().from_lua,
            'to_lua':Kit.Convert().to_lua,
            'from_toml':Kit.Convert().from_toml,
            'to_toml':Kit.Convert().to_toml,
            'as_ip_address': Kit.Convert().as_ip_address,
            'as_ip_segments': Kit.Convert().as_ip_segments,
        }