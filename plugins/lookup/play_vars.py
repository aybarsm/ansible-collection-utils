from __future__ import annotations
from ansible.plugins.lookup import LookupBase
from ansible_collections.aybarsm.utils.plugins.module_utils.tools import Helper

DOCUMENTATION = """
    name: play_vars
    author: aybarsm
    version_added: "0.0.1"
    short_description: Var Dump
    description:
      -  Var Dump
"""

RETURN = """
    _dict:
        type: dict
"""

class LookupModule(LookupBase):
    def run(self, terms, variables, **kwargs):
        ts_raw = Helper.ts()
        ret = {
            'ts': {
                'raw': ts_raw,
                ''
            }
        }

        ret['keys'] = list(variables.keys())
        return [ret]