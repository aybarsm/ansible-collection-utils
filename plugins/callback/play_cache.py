from __future__ import (absolute_import, division, print_function, annotations)
__metaclass__ = type
from typing import Optional
from ansible.plugins.callback import CallbackBase
from ansible.playbook.play import Play
from ansible_collections.aybarsm.utils.plugins.module_utils.tools import PlayCache, Helper, Validate

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
        self._play: Optional[Play] = None
    
    def cache(self) -> Optional[PlayCache]:
        cache = None
        if self._play != None:
            cache = PlayCache.make(self._play.get_variable_manager().get_vars()) #type: ignore

        return cache
    
    def cache_save(self) -> None:
        cache = self.cache()
        if cache:
            cache.save()
    
    def cache_destroy(self) -> None:
        cache = self.cache()
        if cache and cache.persists() != True:
            cache.destroy()

    def v2_runner_on_failed(self, *args, **kwargs):
        self.cache_save()
    
    def v2_runner_on_ok(self, *args, **kwargs):
        self.cache_save()
    
    def v2_runner_on_skipped(self, *args, **kwargs):
        self.cache_save()
    
    def v2_runner_on_unreachable(self, *args, **kwargs):
        self.cache_save()
    
    def v2_runner_on_async_poll(self, *args, **kwargs):
        self.cache_save()
    
    def v2_runner_on_async_ok(self, *args, **kwargs):
        self.cache_save()
    
    def v2_runner_on_async_failed(self, *args, **kwargs):        
        self.cache_save()
    
    def v2_playbook_on_notify(self, *args, **kwargs):
        self.cache_save()
    
    def v2_playbook_on_no_hosts_matched(self, *args, **kwargs):
        self.cache_save()
    
    def v2_playbook_on_no_hosts_remaining(self, *args, **kwargs):        
        self.cache_save()
    
    def v2_playbook_on_task_start(self, *args, **kwargs):
        self.cache_save()
    
    def v2_playbook_on_handler_task_start(self, *args, **kwargs):        
        self.cache_save()
    
    def v2_playbook_on_vars_prompt(self, *args, **kwargs):
        self.cache_save()
    
    def v2_playbook_on_play_start(self, play):
        self._play = play
    
    def v2_playbook_on_stats(self, *args, **kwargs):
        self.cache_destroy()
    
    def v2_on_file_diff(self, *args, **kwargs):
        # self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache_save()
    
    def v2_playbook_on_include(self, *args, **kwargs):
        # self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache_save()
    
    def v2_runner_item_on_ok(self, *args, **kwargs):
        # self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache_save()
    
    def v2_runner_item_on_failed(self, *args, **kwargs):
        # self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache_save()

    def v2_runner_item_on_skipped(self, *args, **kwargs):
        # self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache_save()
    
    def v2_runner_retry(self, *args, **kwargs):
        # self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache_save()
    
    def v2_runner_on_start(self, *args, **kwargs):
        # self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache_save()
        

    