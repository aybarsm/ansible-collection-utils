from types import MappingProxyType as tt_MappingProxyType
from dataclasses import dataclass as dt_dataclass, field as dt_field, MISSING as dt_MISSING
from re import compile as re_compile
import datetime, hashlib


@dt_dataclass(frozen=True, kw_only=True)
class _Sentinel:
    raw: object = dt_field(init=True)
    ts: datetime.datetime = dt_field(init=True)
    ts_str: str = dt_field(init=True)
    ts_safe: str = dt_field(init=True)
    id: str = dt_field(init=True)
    hash: str = dt_field(init=True)

    @staticmethod
    def make() -> "_Sentinel":
        raw_ = object()
        ts_ = datetime.datetime.now(datetime.timezone.utc)
        ts_str_ = str(ts_.strftime('%Y-%m-%dT%H:%M:%SZ'))
        ts_safe_ = str(ts_.strftime('%Y%m%dT%H%M%SZ'))
        id_ = f'{str(id(raw_))}_{str(ts_.strftime('%Y-%m-%dT%H:%M:%S'))}.{ts_.microsecond * 1000:09d}Z'
        hash_ = hashlib.md5(id_.encode()).hexdigest()
        return _Sentinel(raw=raw_, ts=ts_, ts_str=ts_str_, ts_safe=ts_safe_, id=id_, hash=hash_)

class _Kit:
    @staticmethod
    def Ansible():
        import ansible_collections.aybarsm.utils.plugins.module_utils.support.ansible as Ansible
        return Ansible
    
    @staticmethod
    def Convert():
        import ansible_collections.aybarsm.utils.plugins.module_utils.support.convert as Convert
        return Convert

    @staticmethod
    def Data():
        import ansible_collections.aybarsm.utils.plugins.module_utils.support.data as Data
        return Data
    
    @staticmethod
    def Definitions():
        import ansible_collections.aybarsm.utils.plugins.module_utils.support.definitions as Definitions
        return Definitions
    
    @staticmethod
    def Factory():
        import ansible_collections.aybarsm.utils.plugins.module_utils.support.factory as Factory
        return Factory

    @staticmethod
    def Str():
        import ansible_collections.aybarsm.utils.plugins.module_utils.support.str as Str
        return Str

    @staticmethod
    def Utils():
        import ansible_collections.aybarsm.utils.plugins.module_utils.support.utils as Utils
        return Utils

    @staticmethod
    def Validate():
        import ansible_collections.aybarsm.utils.plugins.module_utils.support.validate as Validate
        return Validate
    
    @staticmethod
    def Pydash():
        import pydash
        return pydash
    
    @staticmethod
    def Cerberus():
        import cerberus
        return cerberus
    
    @staticmethod
    def Rich():
        import rich
        return rich
    
    @staticmethod
    def RichPretty():
        import rich.pretty
        return rich.pretty
    
    @staticmethod
    def RichConsole():
        import rich.console
        return rich.console

Sentinel = _Sentinel.make()
Kit = _Kit()
CONF_ = tt_MappingProxyType(
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