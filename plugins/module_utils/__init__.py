### BEGIN: Imports
from types import MappingProxyType as tt_MappingProxyType
from dataclasses import MISSING as dt_MISSING
from re import compile as re_compile
import ansible_collections.aybarsm.utils.plugins.module_utils.support.ansible as Ansible
from ansible_collections.aybarsm.utils.plugins.module_utils.support.collection import Collection
import ansible_collections.aybarsm.utils.plugins.module_utils.support.convert as Convert
import ansible_collections.aybarsm.utils.plugins.module_utils.support.data as Data
from ansible_collections.aybarsm.utils.plugins.module_utils.support._data_query.executor import DataQueryExecutor
import ansible_collections.aybarsm.utils.plugins.module_utils.support.factory as Factory
from ansible_collections.aybarsm.utils.plugins.module_utils.support.fluent import Fluent
from ansible_collections.aybarsm.utils.plugins.module_utils.support.pipe import Pipe
import ansible_collections.aybarsm.utils.plugins.module_utils.support.str as Str
from ansible_collections.aybarsm.utils.plugins.module_utils.support.task import Task, TaskGroup
from ansible_collections.aybarsm.utils.plugins.module_utils.support._task.collection import TaskCollection, TaskCollectionDispatchable
from ansible_collections.aybarsm.utils.plugins.module_utils.support._task.channel import TaskChannel
from ansible_collections.aybarsm.utils.plugins.module_utils.support._task.pipeline import TaskPipeline
import ansible_collections.aybarsm.utils.plugins.module_utils.support.utils as Utils
import ansible_collections.aybarsm.utils.plugins.module_utils.support.validate as Validate
from ansible_collections.aybarsm.utils.plugins.module_utils.support.validator import Validator
### END: Imports
### BEGIN: ImportManager
### END: ImportManager


CONF = tt_MappingProxyType(
    {
        'data_classes': {
            'kwargs': {
                'default': dt_MISSING,
                'default_factory': dt_MISSING,
                'init': True,
                'repr': True,
                'hash': None,
                'compare': True,
                'metadata': None, 
                'kw_only': dt_MISSING,
            },
        },
        'pydantic': {
            'extras': {
                'protected': False,
            },
        },
        'data_query': {
            'defaults': {
                'bindings': {
                    'named': {
                        '_true': True,
                        '_false': False,
                    },
                },
            },
            'test': {
                'prefixes': {
                    'a.b.': "ansible.builtin.",
                    'a.u.': "ansible.utils.",
                    'c.g.': "community.general.",
                    'ayb.a.': 'aybarsm.all.',
                    'ayb.u.': 'aybarsm.utils.',
                },
            },
        },
        'jinja': {
            "prefixes": {
                "a.b.": "ansible.builtin.",
                "a.u.": "ansible.utils.",
                "c.g.": "community.general.",
                "ayb.a.": "aybarsm.all.",
                "ayb.u.": "aybarsm.utils.",
            },
        },
        'validate': {
            "ansible": {
                "entrypoints":
                    [
                        "ansible.cli.adhoc",
                        "ansible_builder.cli",
                        "ansible_collections.ansible_community",
                        "ansible.cli.config",
                        "ansible.cli.console",
                        "ansible.cli.doc",
                        "ansible.cli.galaxy",
                        "ansible.cli.inventory",
                        "ansiblelint.__main__",
                        "ansible.cli.playbook",
                        "ansible.cli.pull",
                        "ansible_test._util.target.cli.ansible_test_cli_stub",
                        "ansible.cli.vault",
                    ]
            },
        },
        'validator': {
            'regex': {
                'ipv4': re_compile(r'^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:\/[1-9]|\/[0-2]\d|\/3[0-2])?$'),
                'ipv4_address': re_compile(r'^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}$'),
                'ipv4_subnet': re_compile(r'^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}\/(?:[1-9]|[0-2]\d|3[0-2])$'),
                'ipv6': re_compile(r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))(?:\/[1-9]|\/[1-9][1-9]|\/1[0-2][0-8])?$'),
                'ipv6_address': re_compile(r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$'),
                'ipv6_subnet': re_compile(r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))\/(?:[1-9]|[1-9][1-9]|1[0-2][0-8])$'),
                'mac_address': re_compile(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'),
                'md5': re_compile(r'^[0-9a-f]{32}$'),
            }
        },
    }
)

__all__ = [
    "Ansible",
    "Collection",
    "Convert",
    "Data",
    "DataQueryExecutor",
    "Factory",
    "Fluent",
    "Pipe",
    "Str",
    "Task", 
    "TaskGroup", 
    "TaskCollection", 
    "TaskCollectionDispatchable",
    "TaskChannel",
    "TaskPipeline",
    "Utils",
    "Validate",
    "Validator",
]