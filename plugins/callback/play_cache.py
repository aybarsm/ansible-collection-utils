from __future__ import (absolute_import, division, print_function, annotations)
__metaclass__ = type
from typing import Optional
from ansible.plugins.callback import CallbackBase
from ansible.playbook.play import Play
from ansible_collections.aybarsm.utils.plugins.module_utils.tools import PlayCache

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
    
    def v2_playbook_on_play_start(self, play):
        self._play = play
    
    def v2_playbook_on_stats(self, *args, **kwargs):
        cache = None if not self._play else PlayCache.make(self._play.get_variable_manager().get_vars()) #type: ignore
        if cache:
            cache.destroy()
    