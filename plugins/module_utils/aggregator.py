from typing import Any as t_Any
from functools import cached_property
from types import MappingProxyType as tt_MappingProxyType
from dataclasses import dataclass as dt_dataclass, field as dt_field, MISSING as dt_MISSING
from re import compile as re_compile
import datetime, hashlib, importlib

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

Sentinel = _Sentinel.make()

class _Kit:
    __container: dict[str, t_Any] = {'_meta': {'errors': [], 'modules': {'loaded': [], 'error': []}}}

    def __add_error(self, message: str) -> None:
        message = message.strip()
        if message == '':
            return
        
        type(self).__container['_meta']['errors'].append(f'[{Sentinel.ts_str}] {message}')

    def __get_module(self, name: str, path: str, of: str = '') -> t_Any:
        name = name.strip().strip('.').strip()
        path = path.strip().strip('.').strip()
        of = of.strip().strip('.').strip()

        if name == '_meta':
            raise ValueError('_meta keyword cannot be used as module name.')
        
        cls = type(self)

        if name not in cls.__container:
            try:
                module = importlib.import_module(path)
            except Exception as e:
                raise ValueError(f"Failed to import {name} from {path}: {e}")
            
            if of != '':
                if getattr(module, of):
                    raise ValueError(f"Failed to import {name} class {of} from {path}: {of} not found in {path}")
                else:
                    module = getattr(module, path)

            cls.__container[name] = module
        
        return cls.__container[name]

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
    
    @property
    def Pydash(self):
        cls = type(self)

        if 'pydash' not in cls.__container:
            import pydash
            cls.__container['pydash'] = pydash
        
        return cls.__container['pydash']
    
    @property
    def Cerberus(self):
        cls = type(self)

        if 'cerberus' not in cls.__container:
            import cerberus
            cls.__container['cerberus'] = cerberus
        
        return cls.__container['cerberus']
    
    @property
    def Rich(self):
        cls = type(self)

        if 'rich' not in cls.__container:
            import rich
            cls.__container['rich'] = rich
        
        return cls.__container['rich']
    
    @property
    def RichPretty(self):
        cls = type(self)

        if 'rich.pretty' not in cls.__container:
            import rich.pretty
            cls.__container['rich.pretty'] = rich.pretty
        
        return cls.__container['rich.pretty']
    
    @cached_property
    def RichConsole(self):
        cls = type(self)

        if 'rich.console' not in cls.__container:
            import rich.console
            cls.__container['rich.console'] = rich.console
        
        return cls.__container['rich.console']

# class _Kit:
#     @cached_property
#     def Ansible(self):
#         import ansible_collections.aybarsm.utils.plugins.module_utils.support.ansible as Ansible
#         return Ansible
    
#     @cached_property
#     def Convert(self):
#         import ansible_collections.aybarsm.utils.plugins.module_utils.support.convert as Convert
#         return Convert

#     @cached_property
#     def Data(self):
#         import ansible_collections.aybarsm.utils.plugins.module_utils.support.data as Data
#         return Data
    
#     @cached_property
#     def Factory(self):
#         import ansible_collections.aybarsm.utils.plugins.module_utils.support.factory as Factory
#         return Factory

#     @cached_property
#     def Str(self):
#         import ansible_collections.aybarsm.utils.plugins.module_utils.support.str as Str
#         return Str

#     @cached_property
#     def Utils(self):
#         import ansible_collections.aybarsm.utils.plugins.module_utils.support.utils as Utils
#         return Utils

#     @cached_property
#     def Validate(self):
#         import ansible_collections.aybarsm.utils.plugins.module_utils.support.validate as Validate
#         return Validate
    
#     @cached_property
#     def Pydash(self):
#         import pydash
#         return pydash
    
#     @cached_property
#     def Cerberus(self):
#         import cerberus
#         return cerberus
    
#     @cached_property
#     def Conf(self) -> tt_MappingProxyType[str, t_Any]:
#         return tt_MappingProxyType(
#             {
#                 'data_classes': {
#                     'kwargs': {
#                         'default': dt_MISSING,
#                         'default_factory': dt_MISSING,
#                         'init': True,
#                         'repr': True,
#                         'hash': None,
#                         'compare': True,
#                         'metadata': None, 
#                         'kw_only': dt_MISSING,
#                     },
#                 },
#                 'pydantic': {
#                     'extras': {
#                         'protected': False,
#                     },
#                 },
#                 'data_query': {
#                     'defaults': {
#                         'bindings': {
#                             'named': {
#                                 '_true': True,
#                                 '_false': False,
#                             },
#                         },
#                     },
#                     'test': {
#                         'prefixes': {
#                             'a.b.': "ansible.builtin.",
#                             'a.u.': "ansible.utils.",
#                             'c.g.': "community.general.",
#                             'ayb.a.': 'aybarsm.all.',
#                             'ayb.u.': 'aybarsm.utils.',
#                         },
#                     },
#                 },
#                 'jinja': {
#                     "prefixes": {
#                         "a.b.": "ansible.builtin.",
#                         "a.u.": "ansible.utils.",
#                         "c.g.": "community.general.",
#                         "ayb.a.": "aybarsm.all.",
#                         "ayb.u.": "aybarsm.utils.",
#                     },
#                     "module_map": {
#                         "AnsibleFilterCore": {"path": "ansible.plugins.filter.core", "class": "FilterModule"},
#                         "AnsibleFilterEncryption": {"path": "ansible.plugins.filter.encryption", "class": "FilterModule"},
#                         "AnsibleFilterMathstuff": {"path": "ansible.plugins.filter.mathstuff", "class": "FilterModule"},
#                         "AnsibleFilterUrls": {"path": "ansible.plugins.filter.urls", "class": "FilterModule"},
#                         "AnsibleFilterUrlsplit": {"path": "ansible.plugins.filter.urls", "class": "FilterModule"},
#                         "AnsibleTestCore": {"path": "ansible.plugins.test.core", "class": "TestModule"},
#                         "AnsibleTestFiles": {"path": "ansible.plugins.test.files", "class": "TestModule"},
#                         "AnsibleTestMathstuff": {"path": "ansible.plugins.test.mathstuff", "class": "TestModule"},
#                         "AnsibleTestUri": {"path": "ansible.plugins.test.uri", "class": "TestModule"},
#                         "AnsibleUtilsTestInAnyNetwork": {"path": "ansible_collections.ansible.utils.plugins.test.in_any_network", "class": "TestModule"},
#                         "AnsibleUtilsTestInNetwork": {"path": "ansible_collections.ansible.utils.plugins.test.in_network", "class": "TestModule"},
#                         "AnsibleUtilsTestInOneNetwork": {"path": "ansible_collections.ansible.utils.plugins.test.in_one_network", "class": "TestModule"},
#                         "AnsibleUtilsTestIp": {"path": "ansible_collections.ansible.utils.plugins.test.ip", "class": "TestModule"},
#                         "AnsibleUtilsTestIpAddress": {"path": "ansible_collections.ansible.utils.plugins.test.ip_address", "class": "TestModule"},
#                         "AnsibleUtilsTestIpv4": {"path": "ansible_collections.ansible.utils.plugins.test.ipv4", "class": "TestModule"},
#                         "AnsibleUtilsTestIpv4Address": {"path": "ansible_collections.ansible.utils.plugins.test.ipv4_address", "class": "TestModule"},
#                         "AnsibleUtilsTestIpv4Hostmask": {"path": "ansible_collections.ansible.utils.plugins.test.ipv4_hostmask", "class": "TestModule"},
#                         "AnsibleUtilsTestIpv4Netmask": {"path": "ansible_collections.ansible.utils.plugins.test.ipv4_netmask", "class": "TestModule"},
#                         "AnsibleUtilsTestIpv6": {"path": "ansible_collections.ansible.utils.plugins.test.ipv6", "class": "TestModule"},
#                         "AnsibleUtilsTestIpv6Address": {"path": "ansible_collections.ansible.utils.plugins.test.ipv6_address", "class": "TestModule"},
#                         "AnsibleUtilsTestIpv6Ipv4Mapped": {"path": "ansible_collections.ansible.utils.plugins.test.ipv6_ipv4_mapped", "class": "TestModule"},
#                         "AnsibleUtilsTestIpv6SixToFour": {"path": "ansible_collections.ansible.utils.plugins.test.ipv6_sixtofour", "class": "TestModule"},
#                         "AnsibleUtilsTestIpv6Teredo": {"path": "ansible_collections.ansible.utils.plugins.test.ipv6_teredo", "class": "TestModule"},
#                         "AnsibleUtilsTestLoopback": {"path": "ansible_collections.ansible.utils.plugins.test.loopback", "class": "TestModule"},
#                         "AnsibleUtilsTestMac": {"path": "ansible_collections.ansible.utils.plugins.test.mac", "class": "TestModule"},
#                         "AnsibleUtilsTestMulticast": {"path": "ansible_collections.ansible.utils.plugins.test.multicast", "class": "TestModule"},
#                         "AnsibleUtilsTestPrivate": {"path": "ansible_collections.ansible.utils.plugins.test.private", "class": "TestModule"},
#                         "AnsibleUtilsTestPublic": {"path": "ansible_collections.ansible.utils.plugins.test.public", "class": "TestModule"},
#                         "AnsibleUtilsTestReserved": {"path": "ansible_collections.ansible.utils.plugins.test.reserved", "class": "TestModule"},
#                         "AnsibleUtilsTestResolvable": {"path": "ansible_collections.ansible.utils.plugins.test.resolvable", "class": "TestModule"},
#                         "AnsibleUtilsTestSubnetOf": {"path": "ansible_collections.ansible.utils.plugins.test.subnet_of", "class": "TestModule"},
#                         "AnsibleUtilsTestSupernetOf": {"path": "ansible_collections.ansible.utils.plugins.test.supernet_of", "class": "TestModule"},
#                         "AnsibleUtilsTestUnspecified": {"path": "ansible_collections.ansible.utils.plugins.test.unspecified", "class": "TestModule"},
#                         "AnsibleUtilsTestValidate": {"path": "ansible_collections.ansible.utils.plugins.test.validate", "class": "TestModule"},
#                         "AnsibleUtilsFilterCidrMerge": {"path": "ansible_collections.ansible.utils.plugins.filter.cidr_merge", "class": "FilterModule"},
#                         "AnsibleUtilsFilterConsolidate": {"path": "ansible_collections.ansible.utils.plugins.filter.consolidate", "class": "FilterModule"},
#                         "AnsibleUtilsFilterFactDiff": {"path": "ansible_collections.ansible.utils.plugins.filter.fact_diff", "class": "FilterModule"},
#                         "AnsibleUtilsFilterFromXml": {"path": "ansible_collections.ansible.utils.plugins.filter.from_xml", "class": "FilterModule"},
#                         "AnsibleUtilsFilterGetPath": {"path": "ansible_collections.ansible.utils.plugins.filter.get_path", "class": "FilterModule"},
#                         "AnsibleUtilsFilterHwaddr": {"path": "ansible_collections.ansible.utils.plugins.filter.hwaddr", "class": "FilterModule"},
#                         "AnsibleUtilsFilterIndexOf": {"path": "ansible_collections.ansible.utils.plugins.filter.index_of", "class": "FilterModule"},
#                         "AnsibleUtilsFilterIp4Hex": {"path": "ansible_collections.ansible.utils.plugins.filter.ip4_hex", "class": "FilterModule"},
#                         "AnsibleUtilsFilterIpaddr": {"path": "ansible_collections.ansible.utils.plugins.filter.ipaddr", "class": "FilterModule"},
#                         "AnsibleUtilsFilterIpcut": {"path": "ansible_collections.ansible.utils.plugins.filter.ipcut", "class": "FilterModule"},
#                         "AnsibleUtilsFilterIpmath": {"path": "ansible_collections.ansible.utils.plugins.filter.ipmath", "class": "FilterModule"},
#                         "AnsibleUtilsFilterIpsubnet": {"path": "ansible_collections.ansible.utils.plugins.filter.ipsubnet", "class": "FilterModule"},
#                         "AnsibleUtilsFilterIpv4": {"path": "ansible_collections.ansible.utils.plugins.filter.ipv4", "class": "FilterModule"},
#                         "AnsibleUtilsFilterIpv6": {"path": "ansible_collections.ansible.utils.plugins.filter.ipv6", "class": "FilterModule"},
#                         "AnsibleUtilsFilterIpv6form": {"path": "ansible_collections.ansible.utils.plugins.filter.ipv6form", "class": "FilterModule"},
#                         "AnsibleUtilsFilterIpwrap": {"path": "ansible_collections.ansible.utils.plugins.filter.ipwrap", "class": "FilterModule"},
#                         "AnsibleUtilsFilterKeepKeys": {"path": "ansible_collections.ansible.utils.plugins.filter.keep_keys", "class": "FilterModule"},
#                         "AnsibleUtilsFilterMacaddr": {"path": "ansible_collections.ansible.utils.plugins.filter.macaddr", "class": "FilterModule"},
#                         "AnsibleUtilsFilterNetworkInNetwork": {"path": "ansible_collections.ansible.utils.plugins.filter.network_in_network", "class": "FilterModule"},
#                         "AnsibleUtilsFilterNetworkInUsable": {"path": "ansible_collections.ansible.utils.plugins.filter.network_in_usable", "class": "FilterModule"},
#                         "AnsibleUtilsFilterNextNthUsable": {"path": "ansible_collections.ansible.utils.plugins.filter.next_nth_usable", "class": "FilterModule"},
#                         "AnsibleUtilsFilterNthhost": {"path": "ansible_collections.ansible.utils.plugins.filter.nthhost", "class": "FilterModule"},
#                         "AnsibleUtilsFilterParamListCompare": {"path": "ansible_collections.ansible.utils.plugins.filter.param_list_compare", "class": "FilterModule"},
#                         "AnsibleUtilsFilterPreviousNthUsable": {"path": "ansible_collections.ansible.utils.plugins.filter.previous_nth_usable", "class": "FilterModule"},
#                         "AnsibleUtilsFilterReduceOnNetwork": {"path": "ansible_collections.ansible.utils.plugins.filter.reduce_on_network", "class": "FilterModule"},
#                         "AnsibleUtilsFilterRemoveKeys": {"path": "ansible_collections.ansible.utils.plugins.filter.remove_keys", "class": "FilterModule"},
#                         "AnsibleUtilsFilterReplaceKeys": {"path": "ansible_collections.ansible.utils.plugins.filter.replace_keys", "class": "FilterModule"},
#                         "AnsibleUtilsFilterSlaac": {"path": "ansible_collections.ansible.utils.plugins.filter.slaac", "class": "FilterModule"},
#                         "AnsibleUtilsFilterToPaths": {"path": "ansible_collections.ansible.utils.plugins.filter.to_paths", "class": "FilterModule"},
#                         "AnsibleUtilsFilterToXml": {"path": "ansible_collections.ansible.utils.plugins.filter.to_xml", "class": "FilterModule"},
#                         "AnsibleUtilsFilterUsableRange": {"path": "ansible_collections.ansible.utils.plugins.filter.usable_range", "class": "FilterModule"},
#                         "AnsibleUtilsFilterValidate": {"path": "ansible_collections.ansible.utils.plugins.filter.validate", "class": "FilterModule"},
#                         "AybarsmUtilsFilters": {"path": "ansible_collections.aybarsm.utils.plugins.filter.filters", "class": "FilterModule"},
#                         "AybarsmUtilsTests": {"path": "ansible_collections.aybarsm.utils.plugins.test.tests", "class": "TestModule"},
#                     }
#                 },
#                 'validate': {
#                     "ansible": {
#                         "entrypoints":
#                             [
#                                 "ansible.cli.adhoc",
#                                 "ansible_builder.cli",
#                                 "ansible_collections.ansible_community",
#                                 "ansible.cli.config",
#                                 "ansible.cli.console",
#                                 "ansible.cli.doc",
#                                 "ansible.cli.galaxy",
#                                 "ansible.cli.inventory",
#                                 "ansiblelint.__main__",
#                                 "ansible.cli.playbook",
#                                 "ansible.cli.pull",
#                                 "ansible_test._util.target.cli.ansible_test_cli_stub",
#                                 "ansible.cli.vault",
#                             ]
#                     },
#                 },
#                 'validator': {
#                     'regex': {
#                         'ipv4': re_compile(r'^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:\/[1-9]|\/[0-2]\d|\/3[0-2])?$'),
#                         'ipv4_address': re_compile(r'^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}$'),
#                         'ipv4_subnet': re_compile(r'^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}\/(?:[1-9]|[0-2]\d|3[0-2])$'),
#                         'ipv6': re_compile(r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))(?:\/[1-9]|\/[1-9][1-9]|\/1[0-2][0-8])?$'),
#                         'ipv6_address': re_compile(r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$'),
#                         'ipv6_subnet': re_compile(r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))\/(?:[1-9]|[1-9][1-9]|1[0-2][0-8])$'),
#                         'mac_address': re_compile(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'),
#                         'md5': re_compile(r'^[0-9a-f]{32}$'),
#                     }
#                 },
#             }
#         )

Kit = _Kit()
# CONF_ = Kit.Conf
# Ansible = Kit.Ansible
# Convert = Kit.Convert
# Data = Kit.Data
# Factory = Kit.Factory
# Str = Kit.Str
# Utils = Kit.Utils
# Validate = Kit.Validate

# Pydash = Kit.Pydash
# Cerberus = Kit.Cerberus

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
            "module_map": {
                "AnsibleFilterCore": {"path": "ansible.plugins.filter.core", "class": "FilterModule"},
                "AnsibleFilterEncryption": {"path": "ansible.plugins.filter.encryption", "class": "FilterModule"},
                "AnsibleFilterMathstuff": {"path": "ansible.plugins.filter.mathstuff", "class": "FilterModule"},
                "AnsibleFilterUrls": {"path": "ansible.plugins.filter.urls", "class": "FilterModule"},
                "AnsibleFilterUrlsplit": {"path": "ansible.plugins.filter.urls", "class": "FilterModule"},
                "AnsibleTestCore": {"path": "ansible.plugins.test.core", "class": "TestModule"},
                "AnsibleTestFiles": {"path": "ansible.plugins.test.files", "class": "TestModule"},
                "AnsibleTestMathstuff": {"path": "ansible.plugins.test.mathstuff", "class": "TestModule"},
                "AnsibleTestUri": {"path": "ansible.plugins.test.uri", "class": "TestModule"},
                "AnsibleUtilsTestInAnyNetwork": {"path": "ansible_collections.ansible.utils.plugins.test.in_any_network", "class": "TestModule"},
                "AnsibleUtilsTestInNetwork": {"path": "ansible_collections.ansible.utils.plugins.test.in_network", "class": "TestModule"},
                "AnsibleUtilsTestInOneNetwork": {"path": "ansible_collections.ansible.utils.plugins.test.in_one_network", "class": "TestModule"},
                "AnsibleUtilsTestIp": {"path": "ansible_collections.ansible.utils.plugins.test.ip", "class": "TestModule"},
                "AnsibleUtilsTestIpAddress": {"path": "ansible_collections.ansible.utils.plugins.test.ip_address", "class": "TestModule"},
                "AnsibleUtilsTestIpv4": {"path": "ansible_collections.ansible.utils.plugins.test.ipv4", "class": "TestModule"},
                "AnsibleUtilsTestIpv4Address": {"path": "ansible_collections.ansible.utils.plugins.test.ipv4_address", "class": "TestModule"},
                "AnsibleUtilsTestIpv4Hostmask": {"path": "ansible_collections.ansible.utils.plugins.test.ipv4_hostmask", "class": "TestModule"},
                "AnsibleUtilsTestIpv4Netmask": {"path": "ansible_collections.ansible.utils.plugins.test.ipv4_netmask", "class": "TestModule"},
                "AnsibleUtilsTestIpv6": {"path": "ansible_collections.ansible.utils.plugins.test.ipv6", "class": "TestModule"},
                "AnsibleUtilsTestIpv6Address": {"path": "ansible_collections.ansible.utils.plugins.test.ipv6_address", "class": "TestModule"},
                "AnsibleUtilsTestIpv6Ipv4Mapped": {"path": "ansible_collections.ansible.utils.plugins.test.ipv6_ipv4_mapped", "class": "TestModule"},
                "AnsibleUtilsTestIpv6SixToFour": {"path": "ansible_collections.ansible.utils.plugins.test.ipv6_sixtofour", "class": "TestModule"},
                "AnsibleUtilsTestIpv6Teredo": {"path": "ansible_collections.ansible.utils.plugins.test.ipv6_teredo", "class": "TestModule"},
                "AnsibleUtilsTestLoopback": {"path": "ansible_collections.ansible.utils.plugins.test.loopback", "class": "TestModule"},
                "AnsibleUtilsTestMac": {"path": "ansible_collections.ansible.utils.plugins.test.mac", "class": "TestModule"},
                "AnsibleUtilsTestMulticast": {"path": "ansible_collections.ansible.utils.plugins.test.multicast", "class": "TestModule"},
                "AnsibleUtilsTestPrivate": {"path": "ansible_collections.ansible.utils.plugins.test.private", "class": "TestModule"},
                "AnsibleUtilsTestPublic": {"path": "ansible_collections.ansible.utils.plugins.test.public", "class": "TestModule"},
                "AnsibleUtilsTestReserved": {"path": "ansible_collections.ansible.utils.plugins.test.reserved", "class": "TestModule"},
                "AnsibleUtilsTestResolvable": {"path": "ansible_collections.ansible.utils.plugins.test.resolvable", "class": "TestModule"},
                "AnsibleUtilsTestSubnetOf": {"path": "ansible_collections.ansible.utils.plugins.test.subnet_of", "class": "TestModule"},
                "AnsibleUtilsTestSupernetOf": {"path": "ansible_collections.ansible.utils.plugins.test.supernet_of", "class": "TestModule"},
                "AnsibleUtilsTestUnspecified": {"path": "ansible_collections.ansible.utils.plugins.test.unspecified", "class": "TestModule"},
                "AnsibleUtilsTestValidate": {"path": "ansible_collections.ansible.utils.plugins.test.validate", "class": "TestModule"},
                "AnsibleUtilsFilterCidrMerge": {"path": "ansible_collections.ansible.utils.plugins.filter.cidr_merge", "class": "FilterModule"},
                "AnsibleUtilsFilterConsolidate": {"path": "ansible_collections.ansible.utils.plugins.filter.consolidate", "class": "FilterModule"},
                "AnsibleUtilsFilterFactDiff": {"path": "ansible_collections.ansible.utils.plugins.filter.fact_diff", "class": "FilterModule"},
                "AnsibleUtilsFilterFromXml": {"path": "ansible_collections.ansible.utils.plugins.filter.from_xml", "class": "FilterModule"},
                "AnsibleUtilsFilterGetPath": {"path": "ansible_collections.ansible.utils.plugins.filter.get_path", "class": "FilterModule"},
                "AnsibleUtilsFilterHwaddr": {"path": "ansible_collections.ansible.utils.plugins.filter.hwaddr", "class": "FilterModule"},
                "AnsibleUtilsFilterIndexOf": {"path": "ansible_collections.ansible.utils.plugins.filter.index_of", "class": "FilterModule"},
                "AnsibleUtilsFilterIp4Hex": {"path": "ansible_collections.ansible.utils.plugins.filter.ip4_hex", "class": "FilterModule"},
                "AnsibleUtilsFilterIpaddr": {"path": "ansible_collections.ansible.utils.plugins.filter.ipaddr", "class": "FilterModule"},
                "AnsibleUtilsFilterIpcut": {"path": "ansible_collections.ansible.utils.plugins.filter.ipcut", "class": "FilterModule"},
                "AnsibleUtilsFilterIpmath": {"path": "ansible_collections.ansible.utils.plugins.filter.ipmath", "class": "FilterModule"},
                "AnsibleUtilsFilterIpsubnet": {"path": "ansible_collections.ansible.utils.plugins.filter.ipsubnet", "class": "FilterModule"},
                "AnsibleUtilsFilterIpv4": {"path": "ansible_collections.ansible.utils.plugins.filter.ipv4", "class": "FilterModule"},
                "AnsibleUtilsFilterIpv6": {"path": "ansible_collections.ansible.utils.plugins.filter.ipv6", "class": "FilterModule"},
                "AnsibleUtilsFilterIpv6form": {"path": "ansible_collections.ansible.utils.plugins.filter.ipv6form", "class": "FilterModule"},
                "AnsibleUtilsFilterIpwrap": {"path": "ansible_collections.ansible.utils.plugins.filter.ipwrap", "class": "FilterModule"},
                "AnsibleUtilsFilterKeepKeys": {"path": "ansible_collections.ansible.utils.plugins.filter.keep_keys", "class": "FilterModule"},
                "AnsibleUtilsFilterMacaddr": {"path": "ansible_collections.ansible.utils.plugins.filter.macaddr", "class": "FilterModule"},
                "AnsibleUtilsFilterNetworkInNetwork": {"path": "ansible_collections.ansible.utils.plugins.filter.network_in_network", "class": "FilterModule"},
                "AnsibleUtilsFilterNetworkInUsable": {"path": "ansible_collections.ansible.utils.plugins.filter.network_in_usable", "class": "FilterModule"},
                "AnsibleUtilsFilterNextNthUsable": {"path": "ansible_collections.ansible.utils.plugins.filter.next_nth_usable", "class": "FilterModule"},
                "AnsibleUtilsFilterNthhost": {"path": "ansible_collections.ansible.utils.plugins.filter.nthhost", "class": "FilterModule"},
                "AnsibleUtilsFilterParamListCompare": {"path": "ansible_collections.ansible.utils.plugins.filter.param_list_compare", "class": "FilterModule"},
                "AnsibleUtilsFilterPreviousNthUsable": {"path": "ansible_collections.ansible.utils.plugins.filter.previous_nth_usable", "class": "FilterModule"},
                "AnsibleUtilsFilterReduceOnNetwork": {"path": "ansible_collections.ansible.utils.plugins.filter.reduce_on_network", "class": "FilterModule"},
                "AnsibleUtilsFilterRemoveKeys": {"path": "ansible_collections.ansible.utils.plugins.filter.remove_keys", "class": "FilterModule"},
                "AnsibleUtilsFilterReplaceKeys": {"path": "ansible_collections.ansible.utils.plugins.filter.replace_keys", "class": "FilterModule"},
                "AnsibleUtilsFilterSlaac": {"path": "ansible_collections.ansible.utils.plugins.filter.slaac", "class": "FilterModule"},
                "AnsibleUtilsFilterToPaths": {"path": "ansible_collections.ansible.utils.plugins.filter.to_paths", "class": "FilterModule"},
                "AnsibleUtilsFilterToXml": {"path": "ansible_collections.ansible.utils.plugins.filter.to_xml", "class": "FilterModule"},
                "AnsibleUtilsFilterUsableRange": {"path": "ansible_collections.ansible.utils.plugins.filter.usable_range", "class": "FilterModule"},
                "AnsibleUtilsFilterValidate": {"path": "ansible_collections.ansible.utils.plugins.filter.validate", "class": "FilterModule"},
                "AybarsmUtilsFilters": {"path": "ansible_collections.aybarsm.utils.plugins.filter.filters", "class": "FilterModule"},
                "AybarsmUtilsTests": {"path": "ansible_collections.aybarsm.utils.plugins.test.tests", "class": "TestModule"},
            }
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