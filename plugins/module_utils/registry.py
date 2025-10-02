_AYBARSM_UTILS = {
    'container': {
        'tools': {},
    },
    'defaults': {
        'tools': {
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
            "jinja": {
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
        },
        'swagger': {
            'settings': {
                'extraction': {
                    'ref_pattern': '.*\\.\\$ref.*$',
                },
                'remap': {
                    'overwrite': False,
                    'ignore_missing': False,
                },
                'combine': {
                    'ansible': {
                        'kwargs': {
                            'recursive': True,
                            'list_merge': 'prepend_rp',
                        },
                    },
                },
                'ansible': {
                    'validation': False,
                    'load_params': False,
                    'kwargs': {
                        'argument_spec': {},
                        'mutually_exclusive': [],
                        'required_one_of': [],
                        'required_together': [],
                        'required_if': [],
                        'required_by': {},
                        'add_file_common_args': False,
                        'supports_check_mode': False,
                    },
                    'fetch_url': {
                        'kwargs': []
                    }
                },
                'defaults': {
                    'header': {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                    },
                },
            },
            'defaults': {
                'url_base': {'type': 'string', 'required': True},
                'docs_source': {'type': 'string', 'required': True},
                'docs_validate_certs': {'type': 'boolean', 'required': False, 'default': True},
                'docs_cache_expires': {'type': 'integer', 'required': False},
                'url_username': {'type': 'string', 'required': False},
                'url_password': {'type': 'string', 'required': False, '_ansible': {'no_log': True}},
                'validate_certs': {'type': 'boolean', 'required': False},
                'use_proxy': {'type': 'boolean', 'required': False},
                'http_agent': {'type': 'string', 'required': False},
                'force_basic_auth': {'type': 'string', 'required': False},
                'client_cert': {'type': 'string', 'required': False},
                'client_key': {'type': 'string', 'required': False},
                'ca_path': {'type': 'string', 'required': False},
                'use_gssapi': {'type': 'boolean', 'required': False},
                'force': {'type': 'boolean', 'required': False},
                'timeout': {'type': 'integer', 'required': False},
                'unix_socket': {'type': 'string', 'required': False},
                'unredirected_headers': {'type': 'array', 'required': False, 'items': {'type': 'string'}},
                'use_netrc': {'type': 'boolean', 'required': False},
                'ciphers': {'type': 'array', 'required': False, 'items': {'type': 'string'}},
                'decompress': {'type': 'boolean', 'required': False},
            },
        }
    }
}

class Registry:
    @staticmethod
    def config():
        import pathlib
        path_root = pathlib.Path(__file__).parent.parent

        return {
            'path': {
                'dir': {
                    'root': str(path_root),
                    'tmp' : str(path_root.joinpath('.tmp')),
                }
            },
            'defaults': _AYBARSM_UTILS['defaults']
        }
    
    @staticmethod
    def register_tool(tool):
        import re
        tool_name = re.sub(r'([A-Z][a-z]+)', r' \1', re.sub(r'([A-Z]+)', r' \1', str(tool.__name__).replace('-', ' ')))
        tool_name = '_'.join(tool_name.split()).lower()
    
        _AYBARSM_UTILS['container']['tools'][tool_name] = tool
    
    @staticmethod
    def load_tools():
        import importlib
        import sys
        import pathlib
        
        # Get the directory containing aggregator.py
        module_dir = pathlib.Path(__file__).parent
        tools_dir = module_dir / 'tools'
        if not tools_dir.is_dir():
            raise ValueError(f"Tools directory not found at {tools_dir}")
        
        # Construct base module path (handles nested packages like ansible_collections...)
        base_module_parts = __name__.split('.')[:-1]  # Removes 'aggregator'
        tools_module = '.'.join(base_module_parts + ['tools'])
        
        loaded_count = 0
        for file_path in tools_dir.glob('*.py'):
            if file_path.stem.startswith('_') or file_path.name == '__init__.py':
                continue
            module_name = f"{tools_module}.{file_path.stem}"
            if module_name in sys.modules:
                continue  # Already loaded; skip to avoid re-execution
            try:
                importlib.import_module(module_name)
                loaded_count += 1
            except ImportError as e:
                # Log or raise; for now, warn and continue
                print(f"Warning: Failed to load {module_name}: {e}")
        
        if loaded_count == 0:
            print("Warning: No tools loaded—check tools directory contents.")
        
    class Tools:
        @staticmethod
        def helper():
            return _AYBARSM_UTILS['container']['tools'].get('helper')
        
        @staticmethod
        def jinja():
            return _AYBARSM_UTILS['container']['tools'].get('jinja')
        
        @staticmethod
        def str():
            return _AYBARSM_UTILS['container']['tools'].get('str')
        
        @staticmethod
        def validate():
            return _AYBARSM_UTILS['container']['tools'].get('validate')

        @staticmethod
        def data():
            return _AYBARSM_UTILS['container']['tools'].get('data')
        
        @staticmethod
        def data_query():
            return _AYBARSM_UTILS['container']['tools'].get('data_query')

        @staticmethod
        def validator():
            return _AYBARSM_UTILS['container']['tools'].get('validator')

# class Aggregator:
#     class tools:
#         validate = Validate
#         helper = Helper
#         str = Str
#         data = Data
#         validator = Validator
#         dataQuery = DataQuery
#         jinja = Jinja
#         typing = typing
#         json = json
#         yaml = yaml
#         re = re
#         pathlib = pathlib
#         abc = abc
#         itertools = itertools
#         requests = requests
#     config = _collection_config()