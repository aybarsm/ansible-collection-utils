from __future__ import annotations
import importlib, re, jinja2
from ansible_collections.aybarsm.utils.plugins.module_utils.tools import Helper

_DEFAULTS = {
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
}

class Jinja:
    jinja2 = jinja2
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Jinja, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
                
        modules = {}
        self._errors = []
        self._loaded = {'filters': {}, 'tests': {}}
        self._prefixes = '(' + ('|'.join(map(lambda op: re.escape(op), list(_DEFAULTS['prefixes'].keys())))) + ')'

        for alias, info in _DEFAULTS['module_map'].items():
            try:
                module = importlib.import_module(info["path"])
                modules[alias] = getattr(module, info["class"])
            except Exception as e:
                self._errors.append(f"Failed to import {alias} from {info['path']}: {e}")
                continue
        
        self.e = jinja2.Environment()
        
        for alias in modules.keys():
            is_test = _DEFAULTS['module_map'][alias]['class'] == 'TestModule'
            segments = str(_DEFAULTS['module_map'][alias]['path']).split('.')
            
            if segments[0] == 'ansible_collections':
                prefix = f'{segments[1]}.{segments[2]}'
            else:
                prefix = 'ansible.builtin'
            
            load_key = 'tests' if is_test else 'filters'
            if prefix not in self._loaded[load_key]:
                self._loaded[load_key][prefix] = []
            
            items = {}
            
            for key, item in (modules[alias]().tests() if is_test else modules[alias]().filters()).items():
                self._loaded[load_key][prefix].append(key)
                items[f'{prefix}.{key}'] = item
            
            if is_test:
                self.e.tests.update(items)
            else:
                self.e.filters.update(items)

    def test_exists(self, test):
        return test in self.e.tests

    def filter_exists(self, filter):
        return filter in self.e.filters
    
    def resolve_op_name(self, op_name):
        return re.compile(f'^{self._prefixes}').sub(lambda match: _DEFAULTS['prefixes'][match.group(0)], op_name)
    
    def test(self, op_name, *args, **kwargs):
        op_name = self.resolve_op_name(op_name)
        if not self.test_exists(op_name):
            raise ValueError(f"Jinja - Test {op_name} does not exist.")
        
        return Helper.callback(self.e.tests[op_name], *args, **kwargs)
    
    def filter(self, op_name, *args, **kwargs):
        op_name = self.resolve_op_name(op_name)
        if not self.filter_exists(op_name):
            raise ValueError(f"Jinja - Test {op_name} does not exist.")
        
        return Helper.callback(self.e.filters[op_name], *args, **kwargs)
    
    def filters(self):
        return self.e.filters
    
    def tests(self):
        return self.e.tests

    def loaded(self):
        return self._loaded
    
    def errors(self):
        return self._errors