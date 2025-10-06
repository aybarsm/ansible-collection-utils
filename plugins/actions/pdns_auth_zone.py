from __future__ import annotations
from ansible.plugins.action import ActionBase
from ansible_collections.aybarsm.utils.plugins.module_utils.powerdns_api import PowerdnsApi, PdnsOperation
from ansible_collections.aybarsm.utils.plugins.module_utils.tools import Data, Validate, Validator, Helper

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars={}):
        pdns = PowerdnsApi(PdnsOperation.auth_zone)
        