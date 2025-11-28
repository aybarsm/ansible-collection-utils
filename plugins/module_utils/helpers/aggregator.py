def __pydash():
    import pydash
    return pydash

def __cerberus():
    import cerberus
    return cerberus

def __ipaddress():
    import ipaddress
    return ipaddress

def __hashlib():
    import hashlib
    return hashlib

def __re():
    import re
    return re

def __inspect():
    import inspect
    return inspect

def __pathlib():
    import pathlib
    return pathlib

### BEGIN: Helpers
def __conf():
    return _CONF

def __ansible():
    import ansible_collections.aybarsm.utils.plugins.module_utils.helpers.ansible as HelperAnsible
    return HelperAnsible

def __convert():
    import ansible_collections.aybarsm.utils.plugins.module_utils.helpers.convert as HelperConvert
    return HelperConvert

def __data():
    import ansible_collections.aybarsm.utils.plugins.module_utils.helpers.data as HelperData
    return HelperData

def __data_query():
    from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.data_query import DataQuery
    return DataQuery

def __factory():
    import ansible_collections.aybarsm.utils.plugins.module_utils.helpers.factory as HelperFactory
    return HelperFactory

def __str():
    import ansible_collections.aybarsm.utils.plugins.module_utils.helpers.str as HelperStr
    return HelperStr

def __types():
    import ansible_collections.aybarsm.utils.plugins.module_utils.helpers.types as HelperTypes
    return HelperTypes

def __utils():
    import ansible_collections.aybarsm.utils.plugins.module_utils.helpers.utils as HelperUtils
    return HelperUtils

def __validate():
    import ansible_collections.aybarsm.utils.plugins.module_utils.helpers.validate as HelperValidate
    return HelperValidate

def __validator():
    from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.validator import Validator
    return Validator
### END: Helpers

_CONF = {
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
            'ipv4': __re().compile(r'^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:\/[1-9]|\/[0-2]\d|\/3[0-2])?$'),
            'ipv4_address': __re().compile(r'^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}$'),
            'ipv4_subnet': __re().compile(r'^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}\/(?:[1-9]|[0-2]\d|3[0-2])$'),
            'ipv6': __re().compile(r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))(?:\/[1-9]|\/[1-9][1-9]|\/1[0-2][0-8])?$'),
            'ipv6_address': __re().compile(r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$'),
            'ipv6_subnet': __re().compile(r'^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))\/(?:[1-9]|[1-9][1-9]|1[0-2][0-8])$'),
            'mac_address': __re().compile(r'^([0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}$'),
            'md5': __re().compile(r'^[0-9a-f]{32}$'),
        }
    },
}