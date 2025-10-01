import sys, abc, types, itertools, typing, os, pathlib, re, json, yaml, inspect, io, datetime, requests
import string, random, math, uuid, tempfile, importlib, urllib, urllib.parse, urllib.error, hashlib
import jinja2, pydash, cerberus, rich.pretty, rich.console
# import jinja2, ansible.errors
from collections.abc import Sequence, MutableSequence, Mapping, MutableMapping

_DEFAULTS_SWAGGER = {
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

_DEFAULTS_TOOLS = {
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
            "a.a.": "aybarsm.all.",
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
}

class Data:
    pydash = pydash
    
    @staticmethod
    def dot(data, prepend='') -> dict:
        ret = {}
        if Validate.is_sequence(data):
            for key, value in enumerate(data):
                new_key = f"{prepend}{str(key)}"
                if value and (Validate.is_mapping(value) or Validate.is_sequence(value)):
                    ret.update(Data.dot(value, new_key + '.'))
                else:
                    ret[new_key] = value
        elif Validate.is_mapping(data):
            for key, value in data.items():
                new_key = f"{prepend}{key}"
                if value and (Validate.is_mapping(value) or Validate.is_sequence(value)):
                    ret.update(Data.dot(value, new_key + '.'))
                else:
                    ret[new_key] = value
        
        return ret

    @staticmethod
    def undot(data: Mapping) -> dict:
        data = dict(data)
        if Validate.blank(data):
            return data
        
        done = []
        ret = {}
        for key, value in data.items():
            if key in done:
                continue
            
            done_iter = [key]
            if Validate.is_mapping(value):
                Data.set(ret, key, Data.undot(value))
            elif '.' not in str(key):
                ret[key] = value
            elif Validate.str_is_int(Str.after_last(key, '.')):
                primary = Str.before_last(key, '.')
                pattern = '^' + re.escape(primary) + '\\.(\\d+)$'
                pattern = re.compile(pattern)
                seq_keys = [seq_key for seq_key in data.keys() if seq_key not in done and pattern.match(seq_key)]
                seq_keys.sort()
                seq = []
                for seq_key in seq_keys:
                    seq.append(data[seq_key])
                done_iter = seq_keys.copy()
                Data.set(ret, primary, seq.copy())
            else:
                Data.set(ret, key, value)
            
            done.extend(done_iter)
        
        return ret
    
    @staticmethod
    def collection():
        return Data.collections()
    
    @staticmethod
    def collections():
        return Data.pydash.collections
    
    @staticmethod
    def get(data, key, default = None):
        return Data.pydash.get(data, key, default)
    
    @staticmethod
    def set(data, key, value):
        return Data.pydash.set_(data, key, value)
    
    @staticmethod
    def has(data, key):
        return Data.pydash.has(data, key)

    @staticmethod
    def forget(data, key):
        return Data.pydash.unset(data, key)

    @staticmethod
    def pluck(data, key):
        return Data.pydash.pluck(data, key)
    
    @staticmethod
    def invert(data):
        return Data.pydash.invert(data)
    
    @staticmethod
    def flip(data):
        return Data.invert(data)
    
    @staticmethod
    def dot_sort_keys(data: Mapping | Sequence, **kwargs) -> dict | list:
        if not Validate.is_sequence(data) and not Validate.is_mapping(data):
            raise ValueError('Invalid data type to sort')
        
        asc = kwargs.pop('asc', True)
        if Validate.is_mapping(data):
            ret = sorted(dict(data).items(), key=lambda item: item[0].count('.'))
        else:
            ret = sorted([item for item in data], key=lambda s: s.count('.'))

        if not asc:
            ret = reversed(ret)
            
        return dict(ret) if Validate.is_mapping(data) else list(ret)

    @staticmethod
    def iterate(data, callback, *args, **kwargs) -> dict | list[dict]:
        Validate.require(['dict', 'iterable_of_dicts'], data, 'data')
        Validate.require(['callable'], callback, 'callback')
        if Validate.blank(data):
            return data
        
        mode = Data.get(kwargs, 'mode', 'filter')
        if mode not in ['filter', 'map']:
            raise ValueError("Data._iterate: Accepted modes are filter, map")
        
        is_map = mode == 'map'
        is_negate = Data.get(kwargs, 'negate', False)
        if is_map and is_negate:
            raise ValueError("Data._iterate: Negate available only for filter mode")
        
        is_dict = Validate.is_dict(data)
        is_keys = Data.get(kwargs, 'keys', False)
        if not is_dict and is_keys:
            raise ValueError("Data._iterate: Keys available only for dicts")
        
        if is_dict and not is_keys:
            return Helper.callback(callback, data)

        ret = {} if is_dict else (data if is_map else [])

        if is_dict:
            for key, value in data.items():
                res = Helper.callback(callback, value, key)
                if is_map:
                    ret[key] = res
                else:
                    res = not res if is_negate else res
                    if res:
                        ret[key] = value
        else:
            for idx in (range(0, len(data))):
                res = Helper.callback(callback, data[idx], idx)
                if is_map:
                    ret[idx] = res
                else:
                    res = not res if is_negate else res
                    if res:
                        ret.append(data[idx]) #type: ignore
        
        return ret

    @staticmethod
    def only_with(data: dict | Sequence[dict], *args, **kwargs) -> Sequence[dict] | list[dict] | dict:
        Validate.require(['dict', 'iterable_of_dicts'], data, 'data')
        Validate.require(['iterable_of_strings'], args, 'args')

        meta = Data.get(kwargs, 'meta', False)
        meta_fix = Data.get(kwargs, 'meta_fix', False)
        no_dot = Data.get(kwargs, 'no_dot', False)
        filled = Data.get(kwargs, 'filled', False)
        if Validate.blank(args) and not meta:
            return data
        
        ret = []
        is_dict = Validate.is_dict(data)
        args = list(args)

        for item in Helper.to_iterable(data):
            keys = args.copy()
            meta_keys = [meta_key for meta_key in item.keys() if str(meta_key).startswith('_')] if meta else []
            if Validate.filled(meta_keys):
                keys.extend(meta_keys)
            
            new_item = {}
            for key in keys:
                key_exists = (no_dot and key in item) or (not no_dot and Data.has(item, key))
                if not key_exists:
                    continue
                
                is_filled = not filled or ((no_dot and Validate.filled(item[key])) or (not no_dot and Validate.filled(Data.get(item, key))))
                if not is_filled:
                    continue

                is_meta = meta and str(key).startswith('_')
                new_key = str(key).lstrip('_') if is_meta and meta_fix else key
                
                if no_dot:
                    new_item[new_key] = item[key]
                else:
                    Data.set(new_item, new_key, Data.get(item, key))
            
            ret.append(new_item)
        
        return ret[0] if is_dict else ret
    
    @staticmethod
    def all_except(data: dict | Sequence[dict], *args, **kwargs) -> Sequence[dict] | list[dict] | dict:
        Validate.require(['dict', 'iterable_of_dicts'], data, 'data')
        Validate.require(['iterable_of_strings'], args, 'args')

        meta = Data.get(kwargs, 'meta', False)
        omitted = Data.get(kwargs, 'omitted', False)
        blank = Data.get(kwargs, 'blank', False)
        no_dot = Data.get(kwargs, 'no_dot', False)
        if Validate.blank(args) and not meta and not omitted and not blank:
            return data

        is_dict = Validate.is_dict(data)
        args = list(args)
        ret = []

        for item in Helper.to_iterable(data):
            keys = args.copy()
            
            exclude_keys = [exc_key for exc_key in item.keys() if str(exc_key).startswith('_')] if meta else []
            if Validate.filled(exclude_keys):
                keys.extend(exclude_keys)
            
            exclude_value_keys = [exc_key for exc_key, exc_value in item.items() if (omitted and Validate.is_omitted(exc_value)) or (blank and Validate.blank(exc_value))] if omitted or blank else []
            if Validate.filled(exclude_value_keys):
                keys.extend(exclude_value_keys)

            new_item = item.copy()
            
            for key in keys:
                key_exists = (no_dot and key in item) or (not no_dot and Data.has(item, key))
                if not key_exists:
                    continue
                
                if no_dot:
                    del new_item[key]
                else:
                    Data.forget(new_item, key)
            
            ret.append(new_item)
        
        return ret[0] if is_dict else ret

    @staticmethod
    def query(data, query, *args, **kwargs):
        dq = DataQuery(query, data, *args, **kwargs)

        return dq.results()
    
    @staticmethod
    def flatten(data, levels=None, skip_nulls=True):
        ret = []
        for element in data:
            if skip_nulls and element in (None, 'None', 'null'):
                continue
            elif Validate.is_sequence(element):
                if levels is None:
                    ret.extend(Data.flatten(element, skip_nulls=skip_nulls))
                elif levels >= 1:
                    ret.extend(Data.flatten(element, levels=(int(levels) - 1), skip_nulls=skip_nulls))
                else:
                    ret.append(element)
            else:
                ret.append(element)

        return ret
    
    @staticmethod
    def merge_hash(x, y, recursive=True, list_merge='replace'):
        Validate.mutable_mappings(x, y)
        
        if x == {} or x == y:
            return y.copy()
        if y == {}:
            return x

        x = x.copy()

        if not recursive and list_merge == 'replace':
            x.update(y)
            return x

        for key, y_value in y.items():
            if key not in x:
                x[key] = y_value
                continue

            x_value = x[key]

            if isinstance(x_value, MutableMapping) and isinstance(y_value, MutableMapping):
                if recursive:
                    x[key] = Data.merge_hash(x_value, y_value, recursive, list_merge)
                else:
                    x[key] = y_value
                continue

            if isinstance(x_value, MutableSequence) and isinstance(y_value, MutableSequence):
                if list_merge == 'replace':
                    x[key] = y_value
                elif list_merge == 'append':
                    x[key] = x_value + y_value #type: ignore
                elif list_merge == 'prepend':
                    x[key] = y_value + x_value #type: ignore
                elif list_merge == 'append_rp':
                    x[key] = [z for z in x_value if z not in y_value] + y_value #type: ignore
                elif list_merge == 'prepend_rp':
                    x[key] = y_value + [z for z in x_value if z not in y_value] #type: ignore
                continue

            x[key] = y_value

        return x
    
    @staticmethod
    def combine(*args, **kwargs):
        recursive = kwargs.pop('recursive', False)
        list_merge = kwargs.pop('list_merge', 'replace')
        reverse = kwargs.pop('reverse', False)

        args = list(args)
        if reverse:
            args.reverse()

        dicts = Data.flatten(args, levels=1)

        if Validate.blank(dicts):
            return {}

        if len(dicts) == 1:
            return dicts[0]

        dicts = reversed(dicts)
        result = next(dicts)
        for dictionary in dicts:
            result = Data.merge_hash(dictionary, result, recursive, list_merge)

        return result
    
    @staticmethod
    def combine_match(data, items, attribute, *args, **kwargs):
        Validate.require('string', data, 'data')
        Validate.require('string', attribute, 'attribute')
        Validate.require(['dict', 'iterable_of_dicts'], items, 'items')        

        is_prepare = kwargs.pop('prepare', False)
        ret = []

        for item in Helper.to_iterable(items):
            pattern = Data.get(item, attribute)
            if not Validate.is_string(pattern) or Validate.blank(pattern):
                continue
                
            if is_prepare:
                pattern = Str.wrap(pattern, '^', '$')
                
            if re.match(rf"{pattern}", data):
                ret.append(item)
        
        if Validate.filled(args):
            ret.extend(list(args))
        
        ret = [Helper.to_safe_json(item) if Validate.is_ansible_mapping(item) else item for item in ret]

        return Data.combine(*ret, **kwargs)

    @staticmethod
    def difference(a: Sequence, b: Sequence, *args: Sequence) -> list:
        if not Validate.is_sequence(a) or not Validate.is_sequence(b):
            raise ValueError('Invalid sequence type')
        
        ret = set(a) - set(b)

        for seq in args:
            if not Validate.is_sequence(seq):
                raise ValueError('Invalid sequence type')
            
            ret = set(ret) - set(seq)
        
        return list(ret)
    
    @staticmethod
    def append(data, key: str, value, **kwargs) -> None:
        is_ioi_extend = kwargs.pop('ioi_extend', False)
        exclude = kwargs.pop('exclude', [])
        is_unique = kwargs.pop('unique', False)

        current = list(Data.get(data, key, []))
        if is_ioi_extend and Validate.is_iterable_of_iterables(value):
            current.extend(value)
        else:
            current.append(value)
        
        if Validate.filled(exclude):
            for exc in exclude:
                exc = Helper.to_iterable(exc)
                current = Data.difference(current, exc)
        
        if is_unique:
            current = list(set(current))

        Data.set(data, key, current.copy())

class DataQuery:
    _op_and = ['&&']
    _op_or = ['||']
    
    def __init__(self, query: str, data: Mapping, *args, **kwargs):
        self._cfg = dict(Data.only_with(kwargs, meta = True, meta_fix = True)) #type: ignore
        self._cfg['patterns'] = { #type: ignore
            'operator': '(' + ('|'.join(map(lambda op: re.escape(op), (self.op_and() + self.op_or())))) + ')', #type: ignore
            'query_parenthese': '\\(\\s*([a-z][a-z0-9_.]*\\s+[a-z][a-z0-9_.]*(?:\\s+(?:\\?|\\:[a-z][a-z0-9_]*))?)\\s*\\)',
        }
        
        self._bindings_pos = []
        self._bindings_named = {}
        self._query_wrap = True
        self._query = ''
        self._data = []
        self._tokens = {}
        self._jinja = Jinja()
        self._results = None
        
        self.prepare(query, args, Data.all_except(kwargs, meta = True))
        self.set_data(data)
        
    def set_data(self, data):        
        self._data = Helper.to_iterable(data)
        self._results = None

    def prepare(self, query, positional_bindings, named_bindings):
        Validate.require('string', query, 'query')
        
        if Validate.blank(query):
            raise ValueError('Query is empty syntax')
        
        query = query.strip()
        
        if query.count('(') != query.count(')'):
            raise ValueError('Invalid query syntax')
        
        Validate.require('iterable', positional_bindings, 'positional_bindings')
        Validate.require('dict', named_bindings, 'named_bindings')
        
        query = re.sub(r'\)', ') ', query)
        query = re.sub(r'\(', '( ', query)
        query = re.sub(r'\(([A-Za-z0-9])', '( \\1', query)
        query = re.sub(r'([A-Za-z0-9?])\)', '\\1 )', query)
        query = re.sub(r'\:+', ':', query)
        query = re.sub(re.compile(f'\\s+{self.patterns('operator')}\\s+'), r' \1 ', query)
        query = re.sub(r'\s+', r' ', query.strip())
        
        query_parenthese = re.compile(self.patterns('query_parenthese', '')) #type: ignore
        while True:
            new_query = query_parenthese.sub(r'\1', query)
            if new_query == query:
                break
            query = new_query
        
        self._query_wrap = True
        if query.startswith('(') and query.endswith(')'):
            self._query_wrap = False
        else:
            query = '( ' + query + ' )'
        
        positional_bindings = list(positional_bindings)
        named_bindings = dict(named_bindings)
        
        if query.count('?') != len(positional_bindings):
            raise ValueError('Invalid number of positional bindings')
        
        b_named = list(set(re.findall(r'[\(+|\s]?:+([A-Za-z0-9_]+)[\)+|\s]?', query)))
        
        if not Validate.contains(named_bindings, *b_named, all = True):
            raise ValueError('Missing named bindings')
        
        self._query = query
        self._bindings_pos = positional_bindings
        self._bindings_named = named_bindings
        self._tokens = self._prepare_tokens()
        self._results = None
    
    def _prepare_tokens(self):
        segments = self._query.split(' ')
        b_pos = 0
        batch = []
        tokens = {}
        master = {'idx': 0, 'next': 1}
        stack = []
        token_key = ''
        
        for idx, segment in enumerate(segments):
            if segment in ['(', ')']:
                if Validate.filled(batch) and not tokens[token_key]['cond']:
                    if not Validate.contains(segments, *(self.op_and() + self.op_or())): #type: ignore
                        tokens[token_key]['cond'] = 'any'
                    else:
                        msg = [segment]
                        if idx > 0:
                            msg.insert(0, segments[idx-1])
                        if idx < len(segments) - 1:
                            msg.append(segments[idx+1])
                        raise ValueError(f'Invalid Syntax: Condition required before opening at segment {token_key} - [{str(idx)}] - {' '.join(msg)}')
                
                if Validate.filled(batch):
                    tokens[token_key]['tests'].append(self._prepare_test_element(*batch))
                    batch = []

                if segment == '(':
                    if idx == 0:
                        if self._query_wrap:
                            stack = [master]
                        else:
                            stack = [{'idx': 1, 'next': 0}]
                            master['next'] = 2
                    else:
                        if len(stack) == 1 and stack[0]['idx'] == 0:
                            stack = []
                            parent = master
                        else:
                            parent = stack[-1]
                        
                        stack.append({'idx': parent['next'], 'next': 0})
                        parent['next'] += 1
                        
                    token_key = '.'.join(str(n['idx']) for n in stack)
                else:
                    stack.pop()
                    
                    if Validate.blank(stack):
                        stack.append(master)

                    token_key = '.'.join(str(n['idx']) for n in stack)
                
                continue
            
            if Validate.blank(token_key):
                raise ValueError('Blank token key')
            
            if token_key not in tokens:
                tokens[token_key] = {'cond': None, 'tests': []}
                if len(stack) > 1:
                    tokens[token_key]['parent'] = '.'.join(str(n['idx']) for n in stack[:-1])
                    # tokens[token_key]['master'] = str(stack[0]['idx'])
                else:
                    tokens[token_key]['parent'] = '0'
                    # tokens[token_key]['parent'] = str(stack[0]['idx'])
                    # tokens[token_key]['master'] = '0'
            
            if segment == '?':
                batch.append(self._bindings_pos[b_pos])
                b_pos += 1
            elif segment.startswith(':'):
                batch.append(self._bindings_named[segment.lstrip(':')])
            elif segment in self.op_and() or segment in self.op_or():
                if not tokens[token_key]['cond']:
                    tokens[token_key]['cond'] = 'all' if segment in self.op_and() else 'any'
                
                if Validate.filled(batch):
                    tokens[token_key]['tests'].append(self._prepare_test_element(*batch))
                
                batch = []
            else:
                batch.append(segment)
            
            if idx == len(segments) - 1 and Validate.filled(batch):
                tokens[token_key]['tests'].append(self._prepare_test_element(*batch))

        return tokens
        # return dict(reversed(dict(sorted(tokens.items(), key=lambda item: item[1]["parent"])).items()))
        # return dict(sorted(tokens.items(), reverse=True))
    
    def _prepare_test_element(self, *args):
        args = Helper.to_iterable(args)
        key = args[0]        
        negate = False
        
        if args[1] == 'not':
            negate = True
            test = args[2]
            after = 3
        else:
            test = args[1]
            after = 2
        
        test_args = args[after:] if len(args) > after else []
        
        return {'test': test, 'key': key, 'args': test_args, 'negate': negate}
        
    
    def _test(self, token, data_idx):
        if Validate.blank(token['tests']):
            return None
        
        is_all = token['cond'] == 'all'
        
        for test in token['tests']:
            args = test['args'].copy()
            args.insert(0, Data.get(self._data[data_idx], test['key']))
            res = self._jinja.test(test['test'], *args)
            res = not res if test['negate'] else res
            if is_all and not res:
                return False
            elif not is_all and res:
                return True
        
        return True if is_all else False

    def _exec(self, first):
        tokens = self.tokens(True)
        token_keys = list(tokens.keys())
        is_all = tokens['0']['cond'] == 'all'
        has_tests = Validate.filled(tokens['0']['tests'])
        ret = []
        
        for idx in range(0, len(self._data)):
            if first and Validate.filled(ret):
                break

            results = {'0': []}
            parent = tokens[token_keys[0]]['parent']
            for key, token in tokens.items():
                if parent != token['parent'] and tokens[parent]['parent'] != '0':
                    is_parent_all = tokens[parent]['cond'] == 'all'
                    results[parent] = [all(results[parent]) if is_parent_all else any(results[parent])]
                elif token['parent'] == '0':
                    if key not in results:
                        results[key] = []
                    
                    if Validate.filled(token['tests']):
                        results[key].append(self._test(token, idx))
                    
                    if key != '0':
                        is_token_all = token['cond'] == 'all'
                        results['0'].append(all(results[key]) if is_token_all else any(results[key]))
                    
                    continue

                parent = token['parent']
                    
                if parent not in results:
                    results[parent] = []
                
                if Validate.filled(token['tests']):
                    results[parent].append(self._test(token, idx))
            
            res = all(results['0']) if is_all else any(results['0'])
            if res:
                ret.append(self._data[idx])
                
        return ret
    
    def results(self):
        default = self.cfg('default', [])
        if Validate.blank(self._data):
            return default
        
        first = self.cfg('first', False)
        Validate.require('bool', first, 'Config: first')
        
        pluck = self.cfg('pluck', [])
        Validate.require('string', 'iterable_of_strings', pluck, 'Config: pluck')
        
        if self._results == None:
            self._results = self._exec(first)
        
        ret = self._results.copy()
        
        if Validate.filled(ret) and Validate.filled(pluck):
            if Validate.is_string(pluck):
                ret = Data.pluck(ret, pluck)
            else:
                ret = Data.only_with(*pluck) #type: ignore
        
        return default if Validate.blank(ret) else (ret[0] if first else ret)

    def _get_value(self, container, key = '', default = None):
        return Data.get(container, key, default) if Validate.filled(key) else container
        
    def query(self):
        return self._query
    
    def cfg(self, key = '', default = None):
        return self._get_value(self._cfg, key, default)
    
    def tokens(self, is_sorted = False):
        if is_sorted:
            tokens = dict(reversed(dict(sorted(self._tokens.items(), key=lambda item: item[1]["parent"])).items()))
        else:
            tokens = self._tokens
        return tokens

    def op_and(self):
        return self.cfg('op_and', self._op_and)

    def op_or(self):
        return self.cfg('op_and', self._op_or)
    
    def patterns(self, key = '', default = None):
        return self._get_value(self.cfg('patterns'), key, default)
    
    def query_wrap(self):
        return self._query_wrap
    
    def data(self):
        return self._data

class Helper:
    @staticmethod
    def save_as_json(content: Mapping | Sequence | str, path: str, **kwargs) -> None:
        overwrite = kwargs.pop('overwrite', False)

        if Validate.file_exists(path) and not overwrite:
            return
        
        if Validate.is_mapping(content):
            content = json.dumps(dict(content), **kwargs)
        elif Validate.is_sequence(content):
            content = json.dumps(list(content), **kwargs)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(str(content))

    @staticmethod
    def path_rglob(path: pathlib.Path | str):
        path = pathlib.Path(path)
        return path.rglob("*")
    
    @staticmethod
    def callable_signature(callback):
        return inspect.signature(callback)
    
    @staticmethod
    def positional_argument_count(callback):
        return int(sum(
            1 for param in Helper.callable_signature(callback).parameters.values()
            if param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ))
    
    @staticmethod
    def required_positional_argument_count(callback):
        return int(sum(
            1 for param in Helper.callable_signature(callback).parameters.values()
            if param.default == inspect.Parameter.empty and
            param.kind in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ))
        
    @staticmethod
    def callable_args_name(callback):
        for name, param in Helper.callable_signature(callback).parameters.items():
            if param.kind == inspect.Parameter.VAR_POSITIONAL:
                return name
        
        return None

    @staticmethod
    def callable_kwargs_name(callback):
        for name, param in Helper.callable_signature(callback).parameters.items():
            if param.kind == inspect.Parameter.VAR_KEYWORD:
                return name
        
        return None
    
    @staticmethod
    def callable_kwargs_defaults(callback):        
        return {
            k: v.default
            for k, v in Helper.callable_signature(callback).parameters.items()
            if v.default is not inspect.Parameter.empty
        }
    
    @staticmethod
    def callback(callback, *args, **kwargs):
        if Helper.callable_args_name(callback) == None:
            take = int(min([len(list(args)), Helper.positional_argument_count(callback)]))
            args = list(list(args)[:take])

        return callback(*args, **kwargs) if Helper.callable_kwargs_name(callback) != None else callback(*args)
    
    @staticmethod
    def join_paths(*args, **kwargs):
        normalize = kwargs.pop('normalize', True)
        
        args = list(args)
        for idx in range(0, len(args)):
            args[idx] = str(args[idx]).strip().rstrip(os.sep).strip()

        ret = os.path.join(*args)
        if normalize:
            ret = os.path.normpath(ret)

        return str(ret)
    
    @staticmethod
    def realpath(path):
        return os.path.realpath(path)
    
    @staticmethod
    def resolve_path(path, **kwargs):
        if kwargs.get('realpath', False):
            path = Helper.realpath(path)
        return path
    
    @staticmethod
    def dump(*args, **kwargs):
        if Validate.is_env_ansible():
            from ansible.utils.display import Display
            buffer = io.StringIO()
            console = rich.console.Console(file=buffer, force_terminal=False)
            for arg in args:
                console.print(rich.pretty.Pretty(arg, **kwargs))

            display = Display()
            display.display(buffer.getvalue())
        else:
            for arg in args:
                rich.pretty.pprint(arg, **kwargs)
    
    @staticmethod
    def ts(**kwargs):
        ts = datetime.datetime.now(datetime.timezone.utc)
        mod = kwargs.get('mod', '')
        
        if mod in ['str', 'string']:
            return str(ts.strftime("%Y-%m-%dT%H:%M:%SZ"))
        elif mod == 'safe':
            return str(ts.strftime("%Y%m%dT%H%M%SZ"))
        elif mod == 'long':
            return str(ts.strftime("%Y-%m-%dT%H:%M:%S") + f".{ts.microsecond * 1000:09d}Z")
        elif mod == 'long_safe':
            return str(ts.strftime("%Y%m%dT%H%M%S") + f".{ts.microsecond * 1000:09d}Z")
        elif mod == 'timestamp':
            return int(ts.timestamp())
        else:
            return ts
    
    @staticmethod
    def placeholder(randLen = 32, **kwargs):
        now = Helper.ts()

        ret = str('|'.join([
            ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(math.ceil(randLen/2))),
            now.strftime("%Y-%m-%dT%H:%M:%S") + f".{now.microsecond * 1000:09d}Z", #type: ignore
            ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(math.floor(randLen/2)))
        ]))

        mod = kwargs.get('mod', '')
        
        if mod in ['hash', 'hashed']:
            return Str.to_md5(ret)
        else:
            return ret
    
    @staticmethod
    def uuid(**kwargs):
        ver = kwargs.get('ver', 4)
        if ver not in [1, 3, 4, 5]:
            raise ValueError(f'Invalid uuid version [{ver}]')
        
        namespace = kwargs.get('namespace', '')
        name = kwargs.get('name', '')
        if ver in [3, 5] and (Validate.blank(namespace) or Validate.blank(name)):
            raise ValueError(f'uuid version [{ver}] requires namespace and name')
        
        raw = kwargs.get('raw', False)
        
        if ver == 1:
            ret = uuid.uuid1()
        elif ver == 3:
            ret = uuid.uuid3(namespace, name)
        elif ver == 4:
            ret = uuid.uuid4()
        elif ver == 5:
            ret = uuid.uuid5(namespace, name)
        
        return ret if raw == True else str(ret)
    
    @staticmethod
    def ensure_directory_exists(path: typing.Union[pathlib.Path, str]) -> None:
        path = pathlib.Path(path)
        path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def path_tmp(path:str, *args, **kwargs) -> str:
        is_dir = kwargs.pop('dir', False)
        args = list(args)
        ensure_directory_exists = is_dir or len(args) > 0
        args = [tempfile.gettempdir(), path] + args
        ret = Helper.join_paths(*args)
        
        if ensure_directory_exists:
            path_dir = ret if is_dir else Helper.dirname(ret)
            Helper.ensure_directory_exists(path_dir)
        
        return ret

    @staticmethod
    def to_ansible_type(data):
        match data:
            case 'str' | 'string':
                return 'str'
            case 'int' | 'integer':
                return 'integer'
            case 'bool' | 'boolean':
                return 'bool'
            case 'float' | 'double' | 'number':
                return 'float'
            case 'list' | 'array' | 'arr':
                return 'list'
            case 'dict' | 'object':
                return 'dict'
            case 'path' | 'file':
                return 'path'
            case _:
                raise ValueError(f"Undefined to_ansible_type: {data}")
    
    @staticmethod
    def to_iterable(data) -> list:
        return list(data) if Validate.is_sequence(data) else [data]
    
    @staticmethod
    def to_querystring(data, keyAttr, valAttr=None, assignChar='=', joinChar='&', recurse=None, recurseIndentSteps=0, recurseIndentChar=' ', repeatJoinCharOnMainLevels=False):
        if Validate.is_dict(data):
            data = [data]

        result = []

        def _to_querystring(innerData, level = 0):
            indent = recurseIndentChar * (level * recurseIndentSteps)
            for item in innerData:
                if keyAttr in item:
                    if repeatJoinCharOnMainLevels and level == 0:
                        result.append('')
                    if valAttr and valAttr in item:
                        result.append(f"{indent}{item[keyAttr]}{assignChar}{item[valAttr]}")
                    else:
                        result.append(f"{indent}{item[keyAttr]}")

                    if recurse and recurse in item and item[recurse]:
                        _to_querystring(item[recurse], level + 1)

        _to_querystring(data)

        return joinChar.join(result).strip(joinChar)
    
    @staticmethod
    def ansible(filter_name, *args, **kwargs):
        jinja = Jinja()
        return jinja.filter(filter_name, *args, **kwargs)
    
    @staticmethod
    def hostvars_to_dict(obj):
        result = {}
        for host in obj:
            try:
                raw_vars = obj.raw_get(host)
                result[host] = Helper.to_safe_json(raw_vars)
            except Exception as e:
                result[host] = f"<error extracting hostvars for {host}: {e}>"
        return result
    
    @staticmethod
    def hostvarsvars_to_dict(obj):
        try:
            return Helper.to_safe_json(obj._vars)
        except Exception as e:
            return f"<error extracting HostVarsVars: {e}>"
    
    @staticmethod
    def lazytemplatedict_to_dict(obj):
        try:
            return Helper.to_safe_json(dict(obj.items()))
        except Exception as e:
            return f"<error extracting HostVarsVars: {e}>"
    
    @staticmethod
    def to_safe_json(data):
        if isinstance(data, (str, int, float, bool)) or data is None:
            return data

        elif Validate.is_hostvars(data):
            return Helper.hostvars_to_dict(data)
        elif Validate.is_hostvarsvars(data):
            return Helper.hostvarsvars_to_dict(data)
        elif Validate.is_lazytemplatedict(data):
            return Helper.lazytemplatedict_to_dict(data)
        elif isinstance(data, dict):
            return {str(k): Helper.to_safe_json(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return [Helper.to_safe_json(item) for item in data]
        elif hasattr(data, '__str__'):
            try:
                return str(data)
            except Exception:
                return "<unserializable object>"

        # Fallback
        return f"<unsupported type: {type(data)}>"
    
    @staticmethod
    def top_level_dirs(paths, *args, **kwargs):
        if Validate.blank(paths):
            return []

        ret = []

        norm_paths = sorted(set(os.path.normpath(p) for p in paths), key=lambda p: p.count(os.sep), reverse=True)
        for path in norm_paths:
            if not any(os.path.commonpath([path, existing]) == path for existing in ret):
                ret.append(path)

        return ret
    
    @staticmethod
    def to_list_dicts(data, defaults={}, *args, **kwargs):
        no_dot = kwargs.get('no_dot', False)
        ret = []

        for keyIndex in range(0, len(data[list(data.keys())[0]])):
            new_item = defaults.copy()

            for dataKey in data.keys():
                if no_dot:
                    new_item[dataKey] = data[dataKey][keyIndex]
                else:
                    Data.set(new_item, dataKey, data[dataKey][keyIndex])

            ret.append(new_item)

        return ret
    
    @staticmethod
    def dirname(path):
        return os.path.dirname(path)

    @staticmethod
    def basename(path):
        return os.path.basename(path)
    
    @staticmethod
    def to_native(*args, **kwargs):
        from ansible.module_utils.common.text.converters import to_native
        return to_native(*args, **kwargs)

    @staticmethod
    def fetch_url_to_module_result(resp, info):
        status = int(info.get('status', -1))

        if status == -1:
            ret = {'fail': True, 'args': [info.get('msg')], 'kwargs': {}}
        elif not (200 <= status < 300):
            err_kwargs = {
                'status': status,
            }
            
            err_body = None
            if Validate.is_http_error(resp):
                err_body = Helper.to_native(info.get('body', ''))
            else:
                err_body = Helper.to_native(resp.read())

            if Validate.filled(err_body):
                err_kwargs['body'] = err_body

            ret = {'fail': True, 'args': [info.get('msg')], 'kwargs': err_kwargs}
        else:
            ret = {'fail': False}
            ret['content'] = Helper.to_native(resp.read())
            
            if Validate.str_is_json(ret['content']):
                ret['content'] = json.loads(ret['content'])
        
        return ret

class Str:
    @staticmethod
    def to_str(data) -> str | list[str]:
        if Validate.is_string(data):
            return data
        
        if Validate.is_iterable(data):
            return [str(item) for item in Helper.to_iterable(data)]
        
        return data

    @staticmethod
    def to_cli(data, *args, **kwargs):
        if not Validate.is_string(data):
            return data

        as_iterable = kwargs.get('iterable', False)
        as_stripped = kwargs.get('stripped', False)
        use_ansible = kwargs.get('use_ansible', False)
        
        ret = data.strip().strip('\'"')

        filter_name = 'from_json' if Validate.is_json_string(ret) else ('from_yaml' if Validate.is_yaml_string(ret) else None)
        if use_ansible and filter_name:
            kwargs = Data.all_except(kwargs, 'iterable', 'stripped', 'use_ansible')
            args = Helper.to_iterable(ret)
            return Helper.ansible(filter_name, *args, **kwargs) #type: ignore
        elif filter_name == 'from_json':
            import json
            return json.load(ret)
        elif filter_name == 'from_yaml':
            import yaml
            return yaml.safe_load(ret)
        elif as_iterable and Validate.contains(ret, ','):
            return [x for x in ','.split((ret if as_stripped else data)) if x]
        elif as_iterable:
            return Helper.to_iterable((ret if as_stripped else data))
        else:
            return Helper.to_iterable(ret if as_stripped else data) if as_iterable else (ret if as_stripped else data)
    
    @staticmethod
    def find(haystack, needle, reverse = False, before = True):
        index = haystack.rfind(needle) if reverse else haystack.find(needle)
        return haystack if index == -1 else (haystack[:index] if before else haystack[index + len(needle):])
    
    @staticmethod
    def before(haystack, needle):
        return Str.find(haystack, needle)
    
    @staticmethod
    def before_last(haystack, needle):
        return Str.find(haystack, needle, reverse = True)
    
    @staticmethod
    def after(haystack, needle):
        return Str.find(haystack, needle, reverse = False, before = False)
    
    @staticmethod
    def after_last(haystack, needle):
        return Str.find(haystack, needle, reverse = True, before = False)
    
    @staticmethod
    def start(haystack, needle):
        if Validate.is_string(needle) and Validate.filled(needle) and not str(haystack).startswith(needle):
            return needle + haystack
        
        return haystack
    
    @staticmethod
    def finish(haystack, needle):
        if Validate.is_string(needle) and Validate.filled(needle) and not str(haystack).endswith(needle):
            return haystack + needle
        
        return haystack
    
    @staticmethod
    def wrap(data, start, finish = None):
        finish = finish if Validate.is_string(finish) else start
        
        return Str.finish(Str.start(data, start), finish)
    
    @staticmethod
    def case_snake(data):
        import re
        s = re.sub(r'([A-Z][a-z]+)', r' \1',
                    re.sub(r'([A-Z]+)', r' \1',
                            data.replace('-', ' ')))
        return '_'.join(s.split()).lower()
    
    @staticmethod
    def to_md5(data):
        return hashlib.md5(str(data).encode()).hexdigest()
    
    @staticmethod
    def url_strip(data):
        return re.sub(r'^https?://', '', str(data))
    
    @staticmethod
    def urlencode(data, **kwargs):
        keys = data.keys()
        for key in keys:
            if Validate.is_bool(data[key]):
                data[key] = 'true' if data[key] else 'false'
        
        return urllib.parse.urlencode(data, **kwargs)
    
    @staticmethod
    def to_tokens(data, *args, **kwargs):
        return data
    
    @staticmethod
    def chop_start(data: str, *args: str) -> str:
        for n in args:
            if data.startswith(n):
                return data[len(n):]
        return data
    
    @staticmethod
    def chop_end(data: str, *args: str) -> str:
        for n in args:
            if data.endswith(n):
                return data[:-len(n)]
        return data
    
    @staticmethod
    def replace(data: str, find: str | list[str], replace: str | list[str], counts: int | list[int] = -1) -> str:
        if Validate.is_iterable(replace):
            if len(Helper.to_iterable(find)) != len(replace):
                raise ValueError('Find and replace length must match when replace is list')
            
            if Validate.is_iterable(counts):
                if len(counts) != len(replace): #type: ignore
                    raise ValueError('Counts and replace length must match when replace is list')
            else:
                counts = [counts] * len(Helper.to_iterable(find)) #type: ignore
        else:
            replace = [replace] * len(find) #type: ignore
            counts = [counts] * len(find) #type: ignore
        
        find = Helper.to_iterable(find)

        for idx in range(0, len(find)):
            data = data.replace(find[idx], replace[idx], counts[idx]) #type: ignore
        
        return data

class Validate:
    @staticmethod
    def is_http_error(data):
        return Validate.is_object(data) and isinstance(data, urllib.error.HTTPError)
    
    @staticmethod
    def is_int_even(data: int) -> bool:
        return data % 2 == 0
    
    @staticmethod
    def is_int_odd(data: int) -> bool:
        return not Validate.is_int_even(data)
    
    @staticmethod
    def is_env_ansible():
        return any(mod in sys.modules for mod in _DEFAULTS_TOOLS['ansible']['entrypoints'])

    @staticmethod
    def is_string(data):
        return isinstance(data, str)

    @staticmethod
    def is_list(data):
        return isinstance(data, list)
    
    @staticmethod
    def is_tuple(data):
        return isinstance(data, tuple)
    
    @staticmethod
    def is_iterable(data: typing.Any, **kwargs) -> bool:
        return Validate.is_sequence(data, **kwargs)
    
    @staticmethod
    def is_dict(data):
        return isinstance(data, dict)
    
    @staticmethod
    def is_bool(data):
        return isinstance(data, bool)
    
    @staticmethod
    def is_object(data):
        return isinstance(data, object)
    
    @staticmethod
    def is_omitted(data):
        return Validate.is_string(data) and str(data).startswith('__omit_place_holder__')
    
    @staticmethod
    def is_defined(data):
        return not Validate.is_undefined(data)
    
    @staticmethod
    def is_undefined(data):
        return Validate.is_object(data) and type(data).__name__.startswith('AnsibleUndefined')
    
    @staticmethod
    def is_hostvars(data):
        return Validate.is_object(data) and type(data).__name__ == 'HostVars'
    
    @staticmethod
    def is_hostvarsvars(data):
        return Validate.is_object(data) and type(data).__name__ == 'HostVarsVars'
    
    @staticmethod
    def is_lazytemplatedict(data):
        return Validate.is_object(data) and type(data).__name__ == '_AnsibleLazyTemplateDict'
    
    @staticmethod
    def is_ansible_mapping(data):
        return Validate.is_hostvars(data) or Validate.is_hostvarsvars(data) or Validate.is_lazytemplatedict(data)
    
    @staticmethod
    def is_int(data):
        return isinstance(data, int)

    @staticmethod
    def is_float(data):
        return isinstance(data, float)
    
    @staticmethod
    def is_none(data):
        return data is None
    
    @staticmethod
    def is_callable(data):
        return callable(data)
    
    @staticmethod
    def is_bytes(data):
        return isinstance(data, bytes)
    
    @staticmethod
    def is_bytearray(data):
        return isinstance(data, bytearray)
    
    @staticmethod
    def is_mapping(data):
        return isinstance(data, Mapping)
    
    @staticmethod
    def is_object_path(data):
        return isinstance(data, pathlib.Path)

    @staticmethod
    def is_sequence(data, include_strings = False):
        if not include_strings and Validate.is_string(data):
            return False
        
        return isinstance(data, Sequence)
    
    @staticmethod
    def is_list_of_dicts(data):
        return Validate.is_list(data) and all(Validate.is_dict(item) for item in data)
    
    @staticmethod
    def is_list_of_lists(data):
        return Validate.is_list(data) and all(Validate.is_list(item) for item in data)
    
    @staticmethod
    def is_list_of_tuples(data):
        return Validate.is_list(data) and all(Validate.is_tuple(item) for item in data)
    
    @staticmethod
    def is_dict_of_lists(data):
        return Validate.is_dict(data) and all(Validate.is_list(item) for item in data.values())
    
    @staticmethod
    def is_dict_of_dicts(data):
        return Validate.is_dict(data) and all(Validate.is_dict(item) for item in data.values())
    
    @staticmethod
    def is_dict_of_iterables(data):
        return Validate.is_dict(data) and all(Validate.is_iterable(item) for item in data.values())

    @staticmethod
    def is_list_of_strings(data):
        return Validate.is_list(data) and all(Validate.is_string(item) for item in data)
    
    @staticmethod
    def is_tuple_of_strings(data):
        return Validate.is_tuple(data) and all(Validate.is_string(item) for item in data)
    
    @staticmethod
    def is_iterable_of_strings(data):
        return Validate.is_iterable(data) and all(Validate.is_string(item) for item in data)
    
    @staticmethod
    def is_iterable_of_iterables(data):
        return Validate.is_iterable(data) and all(Validate.is_iterable(item) for item in data)
    
    @staticmethod
    def is_iterable_of_dicts(data):
        return Validate.is_iterable(data) and all(Validate.is_dict(item) for item in data)
    
    @staticmethod
    def is_list_of_bools(data):
        return Validate.is_list(data) and all(Validate.is_bool(item) for item in data)

    @staticmethod
    def is_blank(data):
        if Validate.is_string(data) and data.strip() == '':
            return True
        elif Validate.is_sequence(data) and len(data) == 0:
            return True
        elif Validate.is_mapping(data) and len(data.keys()) == 0:
            return True
        elif data is None:
            return True
        elif Validate.is_undefined(data):
            return True
        elif Validate.is_omitted(data):
            return True
        
        return False
    @staticmethod
    def is_filled(data):
        return not Validate.is_blank(data)
    
    @staticmethod
    def blank(data):
        return Validate.is_blank(data)
    
    @staticmethod
    def filled(data):
        return Validate.is_filled(data)
    
    @staticmethod
    def contains(data, *args, **kwargs):
        is_all = kwargs.get('all', False)
        args = list(args)
        
        return all([item in data for item in args]) if is_all else any([item in data for item in args])
    
    @staticmethod
    def is_type_of(data, check):
        req = str(check).lower().replace('_', '').replace('-', '')

        match req:
            case 'list':
                return Validate.is_list(data)
            case 'tuple':
                return Validate.is_tuple(data)
            case 'dict':
                return Validate.is_dict(data)
            case 'string':
                return Validate.is_string(data)
            case 'int' | 'integer':
                return Validate.is_int(data)
            case 'float':
                return Validate.is_float(data)
            case 'bool' | 'boolean':
                return Validate.is_bool(data)
            case 'none':
                return Validate.is_none(data)
            case 'listoflists' | 'listoflist':
                return Validate.is_list_of_lists(data)
            case 'listofdicts' | 'listofdict':
                return Validate.is_list_of_dicts(data)
            case 'listofstrings' | 'listofstring':
                return Validate.is_list_of_strings(data)
            case 'iterable':
                return Validate.is_iterable(data)
            case 'iterableofstrings':
                return Validate.is_iterable_of_strings(data)
            case 'listoftuples' | 'listoftuple':
                return Validate.is_list_of_tuples(data)
            case 'listofbooleans' | 'listofboolean' | 'listofbools' | 'listofbool':
                return Validate.is_list_of_bools(data)
            case 'tupleofstrings' | 'tupleofstring':
                return Validate.is_tuple_of_strings(data)
            case 'dictoflists' | 'dictoflist':
                return Validate.is_dict_of_lists(data)
            case 'dictofdicts' | 'dictofdict':
                return Validate.is_dict_of_dicts(data)
            case 'iterableofdicts':
                return Validate.is_iterable_of_dicts(data)
            case 'dictofiterables':
                return Validate.is_dict_of_iterables(data)
            case 'callable':
                return Validate.is_callable(data)
            case _:
                raise ValueError(f"require, {req} is not a valid type to check.")
    
    @staticmethod
    def require(required, data, *args, **kwargs):
        if not (Validate.is_string(required) or Validate.is_iterable_of_strings(required)):
            raise ValueError(f"validate.require, required must be string or iterable of strings, {type(required).__name__} given.")
        
        attr = kwargs.get('attr', '')
        fn = kwargs.get('fn', '')
        all = kwargs.get('all', False) == True

        results = []
        for req in Helper.to_iterable(required):
            results.append(Validate.is_type_of(data, req))

            if results[-1] and not all:
                break
        
        res = all(results) if all else any(results)

        if not res and Validate.filled(attr):
            msg = [
                '' if Validate.blank(fn) else f"{fn} :",
                attr,
                'must be',
                ', '.join(required),
                type(data).__name__,
                'given.'
            ]
            raise ValueError(', '.join(msg))
        
        return False
    
    @staticmethod
    def ansible(op_name, *args, **kwargs):
        jinja = Jinja()
        return jinja.test(op_name, *args, *kwargs)

    @staticmethod
    def is_file(path):
        return os.path.isfile(path)
    
    @staticmethod
    def is_file_readable(path: typing.Union[pathlib.Path, str]) -> bool:
        path = pathlib.Path(path)
        if not path.exists() or not path.is_file():
            return False

        return os.access(path, os.R_OK)
    
    @staticmethod
    def is_file_writable(path: typing.Union[pathlib.Path, str]) -> bool:
        path = pathlib.Path(path)
        if not path.exists() or not path.is_file():
            return False
        
        return os.access(path, os.W_OK)
    
    @staticmethod
    def is_dir(path):
        return os.path.isdir(path)
    
    @staticmethod
    def is_dir_readable(path: typing.Union[pathlib.Path, str]) -> bool:
        path = pathlib.Path(path)
        if not path.exists() or not path.is_dir():
            return False

        return os.access(path, os.R_OK)
    
    @staticmethod
    def is_dir_writable(path: typing.Union[pathlib.Path, str]) -> bool:
        path = pathlib.Path(path)
        if not path.exists() or not path.is_dir():
            return False
        
        return os.access(path, os.W_OK)
    
    @staticmethod
    def path_exists(path):
        return os.path.exists(path)
    
    @staticmethod
    def file_exists(path, **kwargs):
        path = Helper.resolve_path(path, **kwargs)

        return Validate.path_exists(path) and Validate.is_file(path)
    
    @staticmethod
    def dir_exists(path, **kwargs):        
        path = Helper.resolve_path(path, **kwargs)

        return Validate.path_exists(path) and Validate.is_dir(path)
    
    @staticmethod
    def is_json_string(data, type='any'):
        if not Validate.is_string(data):
            return False

        try:
            parsedData = json.loads(data)
            if type == 'object':
                return Validate.is_dict(parsedData)
            elif type == 'array':
                return Validate.is_iterable(parsedData)
            return True
        except (Exception):
            return False
    
    @staticmethod
    def is_yaml_string(data, type='any'):
        if not Validate.is_string(data):
            return False

        try:
            parsedData = yaml.safe_load(data)
            if type == 'object':
                return Validate.is_dict(parsedData)
            elif type == 'array':
                return Validate.is_iterable(parsedData)
            return Validate.is_dict(parsedData) or Validate.is_iterable(parsedData)
        except (Exception):
            return False
    
    @staticmethod
    def callable_has_args(data):        
        Validate.require('callable', data, 'callable')
        
        return Helper.callable_args_name(data) != None

    @staticmethod
    def callable_has_kwargs(data):        
        Validate.require('callable', data, 'callable')
        return Helper.callable_kwargs_name(data) != None
    
    @staticmethod
    def str_is_match(haystack, patterns, *args, **kwargs):
        kwargs = dict(kwargs)
        kwargs['prepare'] = True

        return Validate.str_is_regex(haystack, patterns, *args, **kwargs)

    @staticmethod
    def str_is_regex(haystack, patterns, *args, **kwargs):
        is_cli = kwargs.get('cli', False)
        is_all = kwargs.get('all', False)
        is_escape = kwargs.get('escape', False)
        is_prepare = kwargs.get('prepare', False)

        if is_cli and Validate.is_string(patterns):
            patterns = Str.to_cli(patterns)
        
        if Validate.is_blank(patterns):
            return True

        for pattern in Helper.to_iterable(patterns):
            if is_escape:
                pattern = re.escape(pattern)
            
            if is_prepare:
                pattern = Str.wrap(pattern, '^', '$')
            
            res = re.match(rf"{pattern}", haystack)

            if not is_all and res:
                return True
            elif is_all and not res:
                return False
        
        return is_all
    
    @staticmethod
    def mutable_mappings(a, b):
        if not (isinstance(a, MutableMapping) and isinstance(b, MutableMapping)):
            myvars = []
            for x in [a, b]:
                try:
                    myvars.append(json.dumps(x))
                except Exception:
                    myvars.append(Helper.to_native(x))
            raise ValueError("failed to combine variables, expected dicts but got a '{0}' and a '{1}': \n{2}\n{3}".format(
                a.__class__.__name__, b.__class__.__name__, myvars[0], myvars[1])
            )
    
    @staticmethod
    def str_is_int(data: str) -> bool:
        return re.match(r"^[-]?[0-9]+$", data) != None
    
    @staticmethod
    def str_is_unsigned_int(data: str) -> bool:
        return re.match(r"^[0-9]+$", data) != None
    
    @staticmethod
    def str_is_numeric(data: str) -> bool:
        return re.match(r"^[+-]?(?:(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?|\.\d+)$", data) != None
    
    @staticmethod
    def str_is_url(data: str) -> bool:
        try:
            result = urllib.parse.urlparse(data)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False
    
    @staticmethod
    def str_is_json(data, type='any'):
        if not Validate.is_string(data):
            return False

        try:
            parsedData = json.loads(data)
            if type == 'object':
                return Validate.is_mapping(parsedData)
            elif type == 'array':
                return Validate.is_sequence(parsedData)
            return True
        except (Exception):
            return False
    
    @staticmethod
    def str_is_yaml(data, type='any'):
        if not Validate.is_string(data):
            return False

        try:
            parsedData = yaml.safe_load(data)
            if type == 'object':
                return Validate.is_mapping(parsedData)
            elif type == 'array':
                return Validate.is_sequence(parsedData)
            return Validate.is_mapping(parsedData) or Validate.is_sequence(parsedData)
        except (Exception):
            return False

class Jinja:
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
        self._prefixes = '(' + ('|'.join(map(lambda op: re.escape(op), list(_DEFAULTS_TOOLS['jinja']['prefixes'].keys())))) + ')'

        for alias, info in _DEFAULTS_TOOLS['jinja']['module_map'].items():
            try:
                module = importlib.import_module(info["path"])
                modules[alias] = getattr(module, info["class"])
            except Exception as e:
                self._errors.append(f"Failed to import {alias} from {info['path']}: {e}")
                continue
        
        self.e = jinja2.Environment()
        
        for alias in modules.keys():
            is_test = _DEFAULTS_TOOLS['jinja']['module_map'][alias]['class'] == 'TestModule'
            segments = str(_DEFAULTS_TOOLS['jinja']['module_map'][alias]['path']).split('.')
            
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
        return re.compile(f'^{self._prefixes}').sub(lambda match: _DEFAULTS_TOOLS['jinja']['prefixes'][match.group(0)], op_name)
    
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

class Validator(cerberus.Validator):
    def _validate_path_exists(self, constraint, field, value):
        """{'type': 'boolean'}"""
        if constraint is True and not Validate.path_exists(value):
            self._error(field, f"Must be an [{value}] existing path") #type: ignore
        elif constraint is False and Validate.path_exists(value):
            self._error(field, f"Must be a [{value}] missing path") #type: ignore
    
    def _validate_file_exists(self, constraint, field, value):
        """{'type': 'boolean'}"""
        if constraint is True and not Validate.file_exists(value):
            self._error(field, f"Must be an [{value}] existing file") #type: ignore
        elif constraint is False and Validate.file_exists(value):
            self._error(field, f"Must be a [{value}] missing file") #type: ignore
    
    def _validate_dir_exists(self, constraint, field, value):
        """{'type': 'boolean'}"""
        if constraint is True and not Validate.dir_exists(value):
            self._error(field, f"Must be an [{value}] existing directory") #type: ignore
        elif constraint is False and Validate.dir_exists(value):
            self._error(field, f"Must be a [{value}] missing directory") #type: ignore

    def error_message(self) -> str:
        parts = []
        for key_name, error in (Data.dot(self.errors)).items():
            parts.append(f'{key_name}: {error}')
        
        return ' | '.join(parts)

def _collection_config() -> dict:
    path_root = pathlib.Path(__file__).parent.parent
    return {
        'path': {
            'dir': {
                'root': str(path_root),
                'tmp' : str(path_root.joinpath('.tmp')),
            }
        },
        'defaults': {
            'swagger': _DEFAULTS_SWAGGER
        }
    }

class Aggregator:
    class tools:
        validate = Validate
        helper = Helper
        str = Str
        data = Data
        validator = Validator
        dataQuery = DataQuery
        jinja = Jinja
        typing = typing
        json = json
        yaml = yaml
        re = re
        pathlib = pathlib
        abc = abc
        # ansible_errors = ansible.errors
        itertools = itertools
        requests = requests
    config = _collection_config()