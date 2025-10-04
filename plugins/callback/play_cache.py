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
    
    def cache(self) -> Optional[PlayCache]:
        return self._cache

    def cache_file(self) -> Optional[str]:
        if self._cache_file == None and self._play != None:
            cache_file = self._play.get_variable_manager().get_vars().get('hostvars', {}).get('localhost', {}).get('play_cache__file', '')
            if Validate.filled(cache_file):
                self._cache_file = cache_file
            
        return self._cache_file
    
    def cache_save(self) -> None:
        if self._cache:
            self._cache.save()
    
    def cache_clear(self) -> None:
        if self._cache:
            self._cache.clear()
    
    def cache_destroy(self) -> None:
        if self._cache:
            self._cache.destroy()

    def v2_playbook_on_play_start(self, play):
        self._play = play
        self._cache = PlayCache(self.cache_file()) #type: ignore
        self.cache_clear()
    
    def v2_playbook_on_stats(self, *args, **kwargs):
        # if self._play != None:
        #     Helper.dump(self._play.get_variable_manager().get_vars().get('hostvars', {}).get('localhost', {}).get('play_cache__file', ''))
        #     keys = list(self._play.get_variable_manager().get_vars().get('hostvars', {}).get('localhost', {}).keys())
        #     vars = self._play.get_variable_manager().get_vars().get('hostvars', {}).get('localhost', {})
        #     Helper.dump([vars.get('inventory_file', ''), vars.get('playbook_dir', ''), vars.get('ansible_play_name', ''), vars.get('ansible_play_hosts', '')])
        #    variable_manager = self._play.get_variable_manager()
        #    from ansible.vars.manager import VariableManager
        #    Helper.dump(Helper.to_type_name(variable_manager), variable_manager.__module__)
        #     self._cache_file = self._play.get_variable_manager().get_vars(play=self._play, host='localhost').get('play_cache__file', '')
        # Helper.dump(self.cache_file())
        # self.cache_save()
        # self._cache.destroy()
    
    # def set_options(self, task_keys=None, var_options=None, direct=None):
    #     super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

    #     self._tree_dir = self.get_option('directory')

    # def v2_runner_on_failed(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
    #     self.cache().save()
    
    # def v2_runner_on_ok(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
    #     self.cache().save()
    
    # def v2_runner_on_skipped(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
    #     self.cache().save()
    
    # def v2_runner_on_unreachable(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
    #     self.cache().save()
    
    # def v2_runner_on_async_poll(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
    #     self.cache().save()
    
    # def v2_runner_on_async_ok(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
    #     self.cache().save()
    
    # def v2_runner_on_async_failed(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
    #     self.cache().save()
    
    # def v2_playbook_on_notify(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
    #     self.cache().save()
    
    # def v2_playbook_on_no_hosts_matched(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
    #     self.cache().save()
    
    # def v2_playbook_on_no_hosts_remaining(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
    #     self.cache().save()
    
    # def v2_playbook_on_task_start(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
    #     self.cache().save()
    
    # def v2_playbook_on_handler_task_start(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
    #     self.cache().save()
    
    # def v2_playbook_on_vars_prompt(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
    #     self.cache().save()
    
    
    
    # def v2_on_file_diff(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
    #     self.cache().save()
    
    # def v2_playbook_on_include(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
    #     self.cache().save()
    
    # def v2_runner_item_on_ok(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
    #     self.cache().save()
    
    # def v2_runner_item_on_failed(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
    #     self.cache().save()

    # def v2_runner_item_on_skipped(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
    #     self.cache().save()
    
    # def v2_runner_retry(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
    #     self.cache().save()
    
    # def v2_runner_on_start(self, *args, **kwargs):
    #     self.cache().set(str(Helper.ts(mod='long')), 'any')
    #     self.cache().save()
        

    