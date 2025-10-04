from __future__ import (absolute_import, division, print_function, annotations)
__metaclass__ = type

from ansible.plugins.callback import CallbackBase
from ansible_collections.aybarsm.utils.plugins.module_utils.tools import PlayCache, Helper

DOCUMENTATION = '''
    name: play_cache
    callback_type: notification
    requirements:
        - enable in configuration - callbacks_enabled = aybarsm.utils.play_cache (or tree if not using FQCN)
    short_description: Generates a JSON file per play run and deletes at end
    description:
        - This callback plugin generates a JSON file per play run for caching data.
        - When the playbook is completed, the file is deleted.
'''

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = 'aybarsm.utils.play_cache'
    CALLBACK_NEEDS_ENABLED = True

    def __init__(self, display=None):
        super(CallbackModule, self).__init__(display=display)
        self._cache = PlayCache()
        self._cache_file_suffix = self.cache().cache_file_suffix()
    
    def cache(self)-> PlayCache:
        return self._cache
    
    def cache_file(self)-> str:
        return self.cache().cache_file()
    
    # def set_options(self, task_keys=None, var_options=None, direct=None):
    #     super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

    #     self._tree_dir = self.get_option('directory')

    def v2_runner_on_failed(self, *args, **kwargs):
        self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache().save()
    
    def v2_runner_on_ok(self, *args, **kwargs):
        self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache().save()
    
    def v2_runner_on_skipped(self, *args, **kwargs):
        self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache().save()
    
    def v2_runner_on_unreachable(self, *args, **kwargs):
        self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache().save()
    
    def v2_runner_on_async_poll(self, *args, **kwargs):
        self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache().save()
    
    def v2_runner_on_async_ok(self, *args, **kwargs):
        self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache().save()
    
    def v2_runner_on_async_failed(self, *args, **kwargs):
        self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache().save()
    
    def v2_playbook_on_notify(self, *args, **kwargs):
        self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache().save()
    
    def v2_playbook_on_no_hosts_matched(self, *args, **kwargs):
        self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache().save()
    
    def v2_playbook_on_no_hosts_remaining(self, *args, **kwargs):
        self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache().save()
    
    def v2_playbook_on_task_start(self, *args, **kwargs):
        self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache().save()
    
    def v2_playbook_on_handler_task_start(self, *args, **kwargs):
        self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache().save()
    
    def v2_playbook_on_vars_prompt(self, *args, **kwargs):
        self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache().save()
    
    def v2_playbook_on_play_start(self, *args, **kwargs):
        self.cache().clear()
    
    def v2_playbook_on_stats(self, *args, **kwargs):
        self.cache().save()
        # self._cache.destroy()
    
    def v2_on_file_diff(self, *args, **kwargs):
        self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache().save()
    
    def v2_playbook_on_include(self, *args, **kwargs):
        self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache().save()
    
    def v2_runner_item_on_ok(self, *args, **kwargs):
        self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache().save()
    
    def v2_runner_item_on_failed(self, *args, **kwargs):
        self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache().save()

    def v2_runner_item_on_skipped(self, *args, **kwargs):
        self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache().save()
    
    def v2_runner_retry(self, *args, **kwargs):
        self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache().save()
    
    def v2_runner_on_start(self, *args, **kwargs):
        self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache().save()
        

    