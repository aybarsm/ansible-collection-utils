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
        self._cache_file: Optional[str] = None
        self._cache: Optional[PlayCache] = None
        self._persistent: Optional[bool] = None
    
    def _cache_init(self):
        if not self._cache and self.cache_file():
            self._cache = PlayCache(self.cache_file()) #type: ignore
            self.cache_clear()
    
    def cache(self) -> Optional[PlayCache]:
        return self._cache

    def cache_file(self) -> Optional[str]:
        if self._cache_file == None and self._play != None:
            cache_file = PlayCache.resolve_file(self._play.get_variable_manager().get_vars()) #type: ignore
            if cache_file != None:
                self._cache_file = cache_file
            
        return self._cache_file
    
    def cache_save(self) -> None:
        if self._cache:
            self._cache.save()
        else:
            self._cache_init()
    
    def cache_clear(self) -> None:
        if self._cache:
            self._cache.clear()
        else:
            self._cache_init()
    
    def cache_destroy(self) -> None:
        if self._cache:
            self._cache.destroy()
    
    def is_cache_persistent(self) -> Optional[bool]:
        if self._persistent == None and self._play != None:
            self._persistent = PlayCache.resolve_persistent(self._play.get_variable_manager().get_vars()) #type: ignore
        
        return self._persistent

    def v2_runner_on_failed(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache_save()
    
    def v2_runner_on_ok(self, *args, **kwargs):
        # self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache_save()
    
    def v2_runner_on_skipped(self, *args, **kwargs):
        # self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache_save()
    
    def v2_runner_on_unreachable(self, *args, **kwargs):
        # self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache_save()
    
    def v2_runner_on_async_poll(self, *args, **kwargs):
        # self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache_save()
    
    def v2_runner_on_async_ok(self, *args, **kwargs):
        # self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache_save()
    
    def v2_runner_on_async_failed(self, *args, **kwargs):
        # self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache_save()
    
    def v2_playbook_on_notify(self, *args, **kwargs):
        # self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache_save()
    
    def v2_playbook_on_no_hosts_matched(self, *args, **kwargs):
        # self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache_save()
    
    def v2_playbook_on_no_hosts_remaining(self, *args, **kwargs):
        # self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache_save()
    
    def v2_playbook_on_task_start(self, *args, **kwargs):
        # self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache_save()
    
    def v2_playbook_on_handler_task_start(self, *args, **kwargs):
        # self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache_save()
    
    def v2_playbook_on_vars_prompt(self, *args, **kwargs):
        # self.cache().set(str(Helper.ts(mod='long')), 'any')
        self.cache_save()
    
    def v2_playbook_on_play_start(self, play):
        self._play = play
        self._cache_init()
    
    def v2_playbook_on_stats(self, *args, **kwargs):
        self.cache_save()
        # if not self.is_cache_persistent():
            # self.cache_destroy()
    
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
        

    