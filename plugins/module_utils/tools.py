from __future__ import annotations
from http.client import HTTPResponse
import sys, re, json, yaml, inspect, pathlib, os, io, datetime, random, uuid, string, tempfile, importlib, hashlib, urllib.parse, math, time, errno, copy, base64
import rich.pretty, rich.console, jinja2, cerberus
from typing import Callable, Union, Any, Optional, Iterable
from collections.abc import Mapping, MutableMapping, Sequence, MutableSequence

_CACHE_MODULE = None

_DEFAULTS_TOOLS = {
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
}

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
                else:
                    tokens[token_key]['parent'] = '0'
            
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

class Data:
    @staticmethod
    def filled(data: Mapping|Sequence, key: str, **kwargs) -> bool:
        return Validate.filled(Data.get(data, key, **kwargs))
    
    @staticmethod
    def blank(data: Mapping|Sequence, key: str, **kwargs) -> bool:
        return Validate.blank(Data.get(data, key, **kwargs))
    
    @staticmethod
    def where(data: Mapping|Sequence, callback: Optional[Callable] = None, default: Any = None, **kwargs) -> Any:
        is_negate = kwargs.pop('negate', False)
        is_first = kwargs.pop('first', False)
        is_last = kwargs.pop('last', False)
        is_key = kwargs.pop('key', False)

        if is_first == True and is_last == True:
            raise ValueError('First and last cannot be searched at the same time.')
        
        is_seq = Validate.is_sequence(data)
        data = list(data) if is_seq else dict(data)

        if Validate.blank(data):
            return default

        if is_first and is_seq and not callback:
            return data[0]
        elif is_first and not is_seq and not callback:
            first_key = list(data.keys())[0] #type: ignore
            return data[first_key]
        else:
            ret = [] if is_seq else {}
            iterate = enumerate(data) if is_seq else data.items() #type: ignore
            for key, value in iterate:
                res = Helper.callback(callback, value, key)
                if is_negate:
                    res = not res
                
                if res == True:
                    if is_seq:
                        if is_key:
                            ret.append(key) #type: ignore
                        else:
                            ret.append(value) #type: ignore
                    else:
                        ret[key] = value
                    
                    if is_first:
                        break

        if Validate.blank(ret):
            return default
        
        if is_first or is_last:
            if not is_seq:
                ret_keys = ret.keys() #type: ignore
                return ret[ret_keys[0]] if is_first else ret[ret_keys[-1]] #type: ignore
            else:
                return ret[0] if is_first else ret[-1]

        return ret
    
    @staticmethod
    def reject(data: Mapping|Sequence, callback: Optional[Callable] = None, default: Any = None, **kwargs) -> Any:
        kwargs['negate'] = True
        return Data.where(data, callback, default, **kwargs)

    @staticmethod
    def first(data: Mapping|Sequence, callback: Optional[Callable] = None, default: Any = None, **kwargs) -> Any:
        kwargs['first'] = True
        kwargs['last'] = False
        return Data.where(data, callback, default, **kwargs)

    @staticmethod
    def last(data: Mapping|Sequence, callback: Optional[Callable] = None, default: Any = None, **kwargs) -> Any:
        kwargs['first'] = False
        kwargs['last'] = True
        return Data.where(data, callback, default, **kwargs)
    
    @staticmethod
    def map(data: Sequence|Mapping, callback: Callable, **kwargs)-> list|dict:
        is_mapping = Validate.is_mapping(data)
        
        if is_mapping:
            ret = {}
            is_with_keys = kwargs.pop('with_keys', False)
            for key, value in dict(data).items():
                new_key = Helper.copy(key)
                if is_with_keys:
                    [new_key, new_value] = Helper.callback(callback, value, key)
                else:
                    new_value = Helper.callback(callback, value, key)
                ret[new_key] = new_value
            
            return ret

        ret = []

        if Validate.blank(data):
            return ret
        
        for idx, item in enumerate(Helper.to_iterable(data)):
            ret.append(Helper.callback(callback, item, idx))

        return ret

    @staticmethod
    def keys(data: Mapping|Sequence[Mapping], **kwargs) -> Any:
        ret = []
        is_mapping = Validate.is_mapping(data)
        replace = kwargs.pop('replace', {})
        
        no_dot = kwargs.pop('no_dot', False)
        ph = Helper.placeholder(mod='hashed')

        for item in Helper.to_iterable(data):
            item_new = Helper.copy(item)
        
            for replacement in replace.get('keys', []):
                if not Validate.is_sequence(replacement) or len(replacement) < 2:
                    raise ValueError('Key replacement requires at least 2 elements')
            
                key_from = replacement[0]
                key_to = replacement[1]
                if key_from == key_to:
                    continue

                key_default = ph
                key_exists = (no_dot and key_from in item_new) or (not no_dot and Data.has(item_new, key_from))

                if len(replacement) > 2:
                    key_default = replacement[2]

                value_new = key_default
                if key_exists and no_dot:
                    value_new = item_new[key_from]
                elif key_exists and not no_dot:
                    value_new = Data.get(item_new, key_from)
                
                if value_new == ph:
                    continue

                if no_dot:
                    item_new[key_to] = value_new
                else:
                    Data.set(item_new, key_to, value_new)

                if key_exists and not Validate.is_falsy(replace.get('remove_replaced', True)):
                    if no_dot:
                        del item_new[key_from]
                    else:
                        Data.forget(item_new, key_from)
                
            ret.append(item_new)

        return ret[0] if is_mapping else ret
    
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
    def pop(data: Mapping, *args):
        ret = Data.only_with(data, *args)
        Data.forget(data, list(args))

        return ret
    
    @staticmethod
    def pydash():
        import pydash
        return pydash

    @staticmethod
    def collection():
        return Data.collections()
    
    @staticmethod
    def collections():
        return Data.pydash().collections
    
    @staticmethod
    def get(data, key, default = None):
        return Data.pydash().get(data, key, default)
    
    @staticmethod
    def set(data, key, value):
        return Data.pydash().set_(data, key, value)
    
    @staticmethod
    def has(data, key):
        return Data.pydash().has(data, key)

    @staticmethod
    def forget(data, keys)-> None:
        for key in Helper.to_iterable(keys):
            Data.pydash().unset(data, key)

    @staticmethod
    def append(data, key: str, value, **kwargs) -> Mapping:
        current = list(Data.get(data, key, []))
        is_extend = kwargs.pop('extend', False)
        is_unique = kwargs.pop('unique', False)
        is_sorted = kwargs.pop('sort', False)

        if is_extend:
            current.extend(value)
        else:
            current.append(value)

        if is_unique:
            current = list(set(current))
        
        if is_sorted:
            current = list(sorted(current))
        
        return Data.set(data, key, current.copy())
    
    @staticmethod
    def prepend(data, key: str, value, **kwargs) -> Mapping:
        current = list(Data.get(data, key, []))
        is_extend = kwargs.pop('extend', False)
        is_unique = kwargs.pop('unique', False)
        is_sorted = kwargs.pop('sort', False)

        if is_extend:
            for item in Helper.to_iterable(value):
                current.insert(0, item)
        else:
            current.insert(0, value)

        if is_unique:
            current = list(set(current))
        
        if is_sorted:
            current = list(sorted(current))
        
        return Data.set(data, key, current.copy())

    @staticmethod
    def pluck(data, key):
        return Data.pydash().pluck(data, key)
    
    @staticmethod
    def invert(data):
        return Data.pydash().invert(data)
    
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
    def unique_by(data: Sequence[Mapping], by: Sequence[str] | Callable, **kwargs) -> list[dict]:
        unique_hashes = []
        ret = []
        ph = Helper.placeholder(mod='hashed')
        
        for idx, item in enumerate(data):
            if Validate.is_callable(by):
                unique_hash = Helper.callback(by, item, idx)
            else:
                unique_parts = Data.only_with(item, *by, default_missing=ph, default_blank=ph).values() #type: ignore
                unique_hash = Str.to_md5('|'.join([Helper.to_text(unique_value) for unique_value in unique_parts]))

            if unique_hash not in unique_hashes:
                ret.append(item)
                unique_hashes.append(unique_hash)
        
        return ret

    @staticmethod
    def only_with(data: Mapping | Sequence[dict], *args, **kwargs) -> Sequence[dict] | list[dict] | dict:
        Validate.require(['dict', 'iterable_of_dicts'], data, 'data')
        Validate.require(['iterable_of_strings'], args, 'args')

        meta = Data.get(kwargs, 'meta', False)
        meta_fix = Data.get(kwargs, 'meta_fix', False)
        no_dot = Data.get(kwargs, 'no_dot', False)
        filled = Data.get(kwargs, 'filled', False)
        is_mapping = Validate.is_mapping(data)
        ph = Helper.placeholder(mod='hashed')
        default_missing = Data.get(kwargs, 'default_missing', ph)
        default_blank = Data.get(kwargs, 'default_blank', ph)
        data = dict(data) if is_mapping else Helper.to_iterable(data) #type: ignore
        if Validate.blank(args) and not meta:
            return data
        
        ret = []
        args = list(args)

        for item in Helper.to_iterable(data):
            keys = args.copy()
            meta_keys = [meta_key for meta_key in item.keys() if str(meta_key).startswith('_')] if meta else []
            if Validate.filled(meta_keys):
                keys.extend(meta_keys)
            
            new_item = {}
            for key in keys:
                key_exists = (no_dot and key in item) or (not no_dot and Data.has(item, key))
                new_value = item.get(key) if no_dot else Data.get(item, key)
                if not key_exists:
                    if default_missing != ph:
                        new_value = default_missing
                    else:
                        continue
                
                is_filled = not filled or ((no_dot and Validate.filled(item[key])) or (not no_dot and Validate.filled(Data.get(item, key))))
                if not is_filled:
                    if default_blank != ph:
                        new_value = default_blank
                    else:
                        continue

                is_meta = meta and str(key).startswith('_')
                new_key = str(key).lstrip('_') if is_meta and meta_fix else key
                
                if no_dot:
                    new_item[new_key] = Helper.copy(new_value)
                else:
                    Data.set(new_item, new_key, Helper.copy(new_value))
            
            ret.append(new_item)
        
        return ret[0] if is_mapping else ret
    
    @staticmethod
    def all_except(data: Mapping | Sequence[dict], *args, **kwargs) -> Sequence[dict] | list[dict] | dict:
        Validate.require(['dict', 'iterable_of_dicts'], data, 'data')
        Validate.require(['iterable_of_strings'], args, 'args')

        meta = Data.get(kwargs, 'meta', False)
        omitted = Data.get(kwargs, 'omitted', False)
        blank = Data.get(kwargs, 'blank', False)
        no_dot = Data.get(kwargs, 'no_dot', False)
        is_mapping = Validate.is_mapping(data)
        data = dict(data) if is_mapping else Helper.to_iterable(data) #type: ignore
        if Validate.blank(args) and not meta and not omitted and not blank:
            return data
        
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
        
        return ret[0] if is_mapping else ret

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
    
    # @staticmethod
    # def combine_by(*args, callback: Callable, **kwargs):
    
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
    def intersect(a: Sequence, b: Sequence, *args: Sequence) -> list:
        if not Validate.is_sequence(a) or not Validate.is_sequence(b):
            raise ValueError('Invalid sequence type')
        
        ret = set(a) & set(b)

        for seq in args:
            if not Validate.is_sequence(seq):
                raise ValueError('Invalid sequence type')
            
            ret = set(ret) & set(seq)
        
        return list(ret)

class Helper:
    @staticmethod
    def to_file_hosts(items: list[dict[str,str]], **kwargs)-> list[str]:
        err_duplicates = kwargs.pop('error_on_duplicates', True)

        ret = []
        meta = {'ips': [], 'names': []}
        stages = []
        last_type = None

        for entry in items:
                if 'raw' in entry:
                    if last_type == 'entry' or last_type == None:
                        stages.append({'type': 'raw', 'lines': []})
                    
                    stages[-1]['lines'].append(entry.get('raw'))
                    last_type = 'raw'
                    continue

                ip = str(Data.get(entry, 'ip', '')).strip()
                
                if ip in meta['names']:
                    if err_duplicates:
                        raise ValueError(f'Duplicate value for [{ip}] IP in hosts file')
                    else:
                        continue

                meta['ips'].append(ip)
                ip_prefix = 'IPv' + ('4' if Validate.is_ip_v4(ip) else '6')
                fqdn = str(Data.get(entry, 'fqdn', '')).strip()
                hostname = str(Data.get(entry, 'hostname', '')).strip()

                line = [ip]
                
                if Validate.filled(fqdn):
                    if f'{ip_prefix}:{fqdn}' in meta['names']:
                        if err_duplicates:
                            raise ValueError(f'Duplicate value for {ip_prefix} [{fqdn}] FQDN in hosts file')
                        else:
                            continue
                    meta['names'].append(f'{ip_prefix}:{fqdn}')
                    line.append(fqdn)
                    
                
                if Validate.filled(hostname):
                    if f'{ip_prefix}:{hostname}' in meta['names']:
                        if err_duplicates:
                            raise ValueError(f'Duplicate value for {ip_prefix} [{hostname}] hostname in hosts file')
                        else:
                            continue
                    meta['names'].append(f'{ip_prefix}:{hostname}')
                    line.append(hostname)
                
                if last_type == 'raw' or last_type == None:
                    stages.append({'type': 'entry', 'lines': []})

                stages[-1]['lines'].append(' '.join(line))
                last_type = 'entry'
        
        for stage in stages:
            stage_lines = list(stage['lines'])
            
            if stage['type'] == 'entry':
                stage_lines.sort()
            
            ret.extend(stage_lines)
        
        return ret
    
    @staticmethod
    def to_file_known_hosts(items: list[dict[str,str]], **kwargs)-> list[str]:
        ret = []
        stages = []
        last_type = None

        for entry in items:
                if 'raw' in entry:
                    if last_type == 'entry' or last_type == None:
                        stages.append({'type': 'raw', 'lines': []})
                    
                    stages[-1]['lines'].append(entry.get('raw'))
                    last_type = 'raw'
                    continue
                
                host_ = entry.get('host', '')
                if Validate.filled(host_):
                    line = [host_]
                else:
                    line = ['|'.join(['|1', entry.get('hmac_key', ''), entry.get('hash', '')])]

                line.extend([entry.get('type', ''), entry.get('key', '')])
                
                if last_type == 'raw' or last_type == None:
                    stages.append({'type': 'entry', 'lines': []})

                stages[-1]['lines'].append(' '.join(line))
                last_type = 'entry'
        
        for stage in stages:
            stage_lines = list(stage['lines'])
            
            if stage['type'] == 'entry':
                stage_lines.sort()
            
            ret.extend(stage_lines)
        
        return ret
    
    @staticmethod
    def from_file_hosts(file_content: str)-> list[dict[str,str]]:
        ret = []

        for line in iter(str(file_content).splitlines()):
            normalised = re.sub(r'\s+', ' ', str(line).strip())
            segments = list(normalised.split(maxsplit=2))
            ip = Data.get(segments, '0')
            fqdn = Data.get(segments, '1')
            hostname = Data.get(segments, '2')

            if not Validate.is_ip(ip) or not Validate.filled(fqdn):
                ret.append({'raw': line})
                continue

            item = {'ip': ip}
            if Validate.filled(fqdn) and Validate.filled(hostname):
                item['fqdn'] = fqdn
                item['hostname'] = hostname
            else:
                item['hostname'] = fqdn
            
            ret.append(item)
        
        return ret
    
    @staticmethod
    def from_file_known_hosts(file_content: str)-> list[dict[str,str]]:
        ret = []

        for line in iter(str(file_content).splitlines()):
            normalised = re.sub(r'\s+', ' ', str(line).strip())
            segments = list(normalised.split(maxsplit=2))
            hash_ = str(Data.get(segments, '0', ''))
            type_ = str(Data.get(segments, '1', ''))
            key_ = str(Data.get(segments, '2', ''))

            if Validate.blank(hash_) or Validate.blank(type_) or Validate.blank(key_) or not type_.startswith('ssh-'):
                ret.append({'raw': line})
                continue

            if hash_.startswith('|1|'):
                hash_segments = list(Str.chop_start(hash_, '|1|').split(sep='|', maxsplit=2))
                hmac_key = str(Data.get(hash_segments, '0', ''))
                hmac_hash = str(Data.get(hash_segments, '1', ''))
                if Validate.blank(hmac_key) or Validate.blank(hmac_hash):
                    raise ValueError(f'Unable to resolve known_hosts hash [{hash_}]')

                item = {
                    'hmac_key': hmac_key,
                    'hash': hmac_hash,
                }
            else:
                item = {
                    'host': hash_
                }
            
            item['type'] = type_
            item['key'] = key_
            ret.append(item)
        
        return ret
    
    @staticmethod
    def to_hash_host_key(host_: str, type_: str, key_: str, **kwargs)-> dict|str:
        import hmac
        as_entry = Validate.truthy(kwargs.pop('as_entry', False))

        key = f'{type_.strip()} {key_.strip()}'
        hmac_key = os.urandom(20)
        hashed_host = hmac.new(hmac_key, Helper.to_bytes(host_), hashlib.sha1).digest() #type: ignore
        
        hmac_key = Helper.to_native(base64.b64encode(hmac_key))
        hashed_host = Helper.to_native(base64.b64encode(hashed_host))
        
        if as_entry:
            return {'hmac_key': hmac_key, 'hash': hashed_host}
        
        parts = key.strip().split()
        # @ indicates the optional marker field used for @cert-authority or @revoked
        i = 1 if parts[0][0] == '@' else 0
        parts[i] = '|1|%s|%s' % (hmac_key, hashed_host)
        return ' '.join(parts)
    
    @staticmethod
    def to_known_host_entry(host_: str, type_: str, key_: str, **kwargs):
        is_hashed = Validate.truthy(kwargs.pop('hashed', False))
        
        if is_hashed:
            ret = Helper.to_hash_host_key(host_, type_, key_, as_entry=True)
            Data.set(ret, '_meta.host', host_)
        else:
            ret = {'host': host_}
        
        ret['key'] = key_
        ret['type'] = type_

        return ret

    @staticmethod
    def get_uid()-> int:
        return os.getuid()
    
    @staticmethod
    def get_uname()-> str:
        import pwd
        return pwd.getpwuid(Helper.get_uid()).pw_name
    
    @staticmethod
    def get_gid()-> int:
        return os.getgid()
    
    @staticmethod
    def get_gname()-> str:
        import grp
        return grp.getgrgid(Helper.get_gid()).gr_name
    
    @staticmethod
    def get_temp_var_name()-> str:
        return f'__tmp_var_{Helper.placeholder(mod='hashed')}'

    @staticmethod
    def ansible_template(templar, variable, **kwargs)-> Any:
        from ansible.template import is_trusted_as_template, trust_as_template 
        extra_vars = kwargs.pop('extra_vars', {})
        remove_extra_vars = kwargs.pop('remove_extra_vars', True)

        if Validate.is_string(variable) and not is_trusted_as_template(variable):
            variable = trust_as_template(variable)
        
        for var_key, var_value in extra_vars.items():
            templar.available_variables[var_key] = var_value
        
        ret = templar.template(variable, **kwargs)
        
        if not Validate.falsy(remove_extra_vars):
            for var_key, var_value in extra_vars.items():
                del templar.available_variables[var_key]
        
        return ret

    @staticmethod
    def to_ansible_vault(templar, data: str, secret: str, is_vault: bool = True, **kwargs)-> str:
        var_data = Helper.get_temp_var_name()
        var_secret = Helper.get_temp_var_name()
        filter_suffix = 'vault' if is_vault else 'unvault'
        variable = '{{ ' + f"{var_data} | ansible.builtin.{filter_suffix}({var_secret})" + ' }}'
        
        kwargs = dict(kwargs)
        Data.set(kwargs, f'extra_vars.{var_data}', data)
        Data.set(kwargs, f'extra_vars.{var_secret}', secret)
        Data.set(kwargs, f'remove_extra_vars', True)
        
        return Helper.ansible_template(templar, variable, **kwargs)
    
    @staticmethod
    def ansible_vault(templar, data: str, secret: str, **kwargs)-> str:        
        return Helper.to_ansible_vault(templar, data, secret, True, **kwargs)

    @staticmethod
    def ansible_unvault(templar, data: str, secret: str, **kwargs)-> str:        
        return Helper.to_ansible_vault(templar, data, secret, False, **kwargs)

    @staticmethod
    def b64_encode(data)-> str:
        data = Helper.to_text(data)
        return base64.b64encode(data.encode("utf-8"))

    @staticmethod
    def b64_decode(data)-> str:
        data = Helper.to_text(data)
        return base64.b64decode(data).decode("utf-8")
    
    @staticmethod
    def to_datettime_from_format(data: str, format_: str, **kwargs) -> datetime.datetime:
        ret = datetime.datetime.strptime(data, format_)
        
        tzinfo_ = kwargs.pop('tzinfo', None)
        if Validate.filled(tzinfo_):
            ret = ret.replace(tzinfo=getattr(datetime.timezone, tzinfo_))
        
        return ret
    
    @staticmethod
    def ensure_utc_timezone(timestamp: datetime.datetime) -> datetime.datetime:
        if timestamp.tzinfo is datetime.timezone.utc:
            return timestamp
        if timestamp.tzinfo is None:
            # We assume that naive datetime objects use timezone UTC!
            return timestamp.replace(tzinfo=datetime.timezone.utc)
        return timestamp.astimezone(datetime.timezone.utc)

    @staticmethod
    def remove_timezone(timestamp: datetime.datetime) -> datetime.datetime:
        # Convert to native datetime object
        if timestamp.tzinfo is None:
            return timestamp
        if timestamp.tzinfo is not datetime.timezone.utc:
            timestamp = timestamp.astimezone(datetime.timezone.utc)
        return timestamp.replace(tzinfo=None)

    @staticmethod
    def add_or_remove_timezone(
        timestamp: datetime.datetime, *, with_timezone: bool
    ) -> datetime.datetime:
        return (
            Helper.ensure_utc_timezone(timestamp) if with_timezone else Helper.remove_timezone(timestamp)
        )
    
    @staticmethod
    def crypto_convert_relative_to_datetime(
        relative_time_string: str,
        *,
        with_timezone: bool = False,
        now: datetime.datetime | None = None,
    ) -> datetime.datetime | None:
        """Get a datetime.datetime or None from a string in the time format described in sshd_config(5)"""

        parsed_result = re.match(
            r"^(?P<prefix>[+-])((?P<weeks>\d+)[wW])?((?P<days>\d+)[dD])?((?P<hours>\d+)[hH])?((?P<minutes>\d+)[mM])?((?P<seconds>\d+)[sS]?)?$",
            relative_time_string,
        )

        if parsed_result is None or len(relative_time_string) == 1:
            # not matched or only a single "+" or "-"
            return None

        offset = datetime.timedelta(0)
        if parsed_result.group("weeks") is not None:
            offset += datetime.timedelta(weeks=int(parsed_result.group("weeks")))
        if parsed_result.group("days") is not None:
            offset += datetime.timedelta(days=int(parsed_result.group("days")))
        if parsed_result.group("hours") is not None:
            offset += datetime.timedelta(hours=int(parsed_result.group("hours")))
        if parsed_result.group("minutes") is not None:
            offset += datetime.timedelta(minutes=int(parsed_result.group("minutes")))
        if parsed_result.group("seconds") is not None:
            offset += datetime.timedelta(seconds=int(parsed_result.group("seconds")))

        if now is None:
            now = Helper.ts() #type: ignore
        else:
            now = Helper.add_or_remove_timezone(now, with_timezone=with_timezone)

        if parsed_result.group("prefix") == "+":
            return now + offset #type: ignore
        return now - offset #type: ignore

    @staticmethod
    def crypto_get_relative_time_option(
        input_string: str,
        *,
        input_name: str,
        with_timezone: bool = False,
        now: datetime.datetime | None = None,
    ) -> datetime.datetime:
        """
        Return an absolute timespec if a relative timespec or an ASN1 formatted
        string is provided.

        The return value will be a datetime object.
        """
        result = Helper.to_text(input_string)
        if result is None:
            raise ValueError(
                f'The timespec "{input_string}" for {input_name} is not valid'
            )
        # Relative time
        if result.startswith("+") or result.startswith("-"):
            res = Helper.crypto_convert_relative_to_datetime(result, with_timezone=with_timezone, now=now)
            if res is None:
                raise ValueError(
                    f'The timespec "{input_string}" for {input_name} is invalid'
                )
            return res
        # Absolute time
        for date_fmt, length in [
            (
                "%Y%m%d%H%M%SZ",
                15,
            ),  # this also parses '202401020304Z', but as datetime(2024, 1, 2, 3, 0, 4)
            ("%Y%m%d%H%MZ", 13),
            (
                "%Y%m%d%H%M%S%z",
                14 + 5,
            ),  # this also parses '202401020304+0000', but as datetime(2024, 1, 2, 3, 0, 4, tzinfo=...)
            ("%Y%m%d%H%M%z", 12 + 5),
        ]:
            if len(result) != length:
                continue
            try:
                res = datetime.datetime.strptime(result, date_fmt)
            except ValueError:
                pass
            else:
                return Helper.add_or_remove_timezone(res, with_timezone=with_timezone)

        raise ValueError(
            f'The time spec "{input_string}" for {input_name} is invalid'
        )
    
    @staticmethod
    def replace_stubs(data: str, replacements: Mapping)-> str:
        ret = re.sub('}+', '}', re.sub(r'{+', '{', data))

        replacements = dict(replacements)
        for key, val in replacements.items():
            key = re.sub('}', '', re.sub(r'{', '', key))
            ret = ret.replace(f'{{{key}}}', str(Helper.to_text(val)))
        
        return ret

    @staticmethod
    def items_to_mapping_by(data: Sequence, callback: Callable)-> dict:
        ret = {}

        for idx, item in data:
            [key, value] = Helper.callback(callback, item, idx)
            Data.set(ret, key, value)
        
        return ret

    @staticmethod
    def mapping_to_items(data: Mapping, key_name='key', value_name='value')-> list:
        data = dict(data)

        ret = []
        for key, value in data.items():
            new_item = {}
            Data.set(new_item, key_name, key)
            Data.set(new_item, value_name, value)
            ret.append(Helper.copy(new_item))
        
        return ret

    @staticmethod
    def group_by(data: Sequence[Mapping], by: Callable | str, **kwargs)-> dict:
        key_default = kwargs.pop('default', 'Z_UNKNOWN')
        ret = {}

        for idx, value in enumerate(data):
            if Validate.is_callable(by):
                key_group = Helper.callback(by, value, idx)
            else:
                key_group = Data.get(value, by)

            if Validate.blank(key_group):
                key_group = key_default

            Data.append(ret, str(key_group), value)

        return ret

    @staticmethod
    def dictsort(data: Mapping, **kwargs)-> dict:
        using = kwargs.pop('using', None)
        
        if Validate.is_callable(using):
            return dict(sorted(data, key=using, **kwargs))

        return dict(sorted(dict(data).items(), **kwargs))

    @staticmethod
    def to_conf(data: Mapping, **kwargs)-> list:
        list_strategy = kwargs.pop('list_strategy', 'join')
        if list_strategy not in ['join', 'iterate_key']:
            raise ValueError('Invalid list_strategy option. Available: join, iterate_key')
        
        keep_meta = kwargs.pop('meta', False)
        char_join = str(kwargs.pop('char_join', ', '))
        char_set = str(kwargs.pop('char_set', ' = '))
        list_unique = kwargs.pop('list_unique', False)
        
        if kwargs.pop('sorted', False) == True:
            data = dict(sorted(dict(data).items()))
        else:
            data = dict(data)

        ret = []
        
        for key, val in data.items():
            key = str(key)
            if key.startswith('_') and not keep_meta:
                continue
            
            if Validate.is_sequence(val):
                val = Data.map(val, lambda val_: str(val_))
                if list_unique:
                    val = list(set(val))

                if list_strategy == 'join':
                    ret.append(f'{key}{char_set}{char_join.join(val)}')
                else:
                    for val_inner in val:
                        ret.append(f'{key}{char_set}{val_inner}')
            else:
                ret.append(f'{key}{char_set}{str(val)}')

        return ret
    
    @staticmethod
    def as_validated_ip_segments(data, on_invalid: Optional[Callable] = None, **kwargs)-> list:
        ret = Data.map(Helper.to_iterable(data), lambda ip_: Helper.ip_as_segments(ip_))

        if Validate.filled(ret) and Validate.filled(on_invalid):
            for idx, item in enumerate(ret):
                if Data.get(item, 'ctrl.valid') == True:
                    continue
                
                e = Helper.callback(on_invalid, item, idx)
                if Validate.is_exception(e):
                    raise e
            
        return list(ret)

    @staticmethod
    def copy(data):
        if Validate.is_deepcopyable(data):
            return copy.deepcopy(data)
        elif Validate.is_copyable(data):
            return copy.copy(data)
        else:
            return data

    @staticmethod
    def random_mac(value, seed=None):
        if not isinstance(value, str):
            raise ValueError(f'Invalid value type ({type(value)}) for random_mac ({value})')

        value = value.lower()
        mac_items = value.split(':')

        if len(mac_items) > 5:
            raise ValueError(f'Invalid value ({value}) for random_mac: 5 colon(:) separated items max')

        err = ""
        for mac in mac_items:
            if not mac:
                err += ",empty item"
                continue
            if not re.match('[a-f0-9]{2}', mac):
                err += f",{mac} not hexa byte"
        err = err.strip(',')

        if err:
            raise ValueError(f'Invalid value ({value}) for random_mac: {err}')

        from random import Random, SystemRandom
        if seed is None:
            r = SystemRandom()
        else:
            r = Random(seed)
        
        v = r.randint(68719476736, 1099511627775)
        remain = 2 * (6 - len(mac_items))
        rnd = f'{v:x}'[:remain]
        return value + re.sub(r'(..)', r':\1', rnd)

    @staticmethod
    def first_filled(*args, default: Any = None)-> Any:
        for arg in args:
            if Validate.filled(arg):
                return arg
        
        return default
    
    @staticmethod
    def ipaddr(value, query: str = ''):
        from ansible_collections.ansible.utils.plugins.plugin_utils.base.ipaddr_utils import ipaddr
        return ipaddr(value, query)

    @staticmethod
    def ip_cidr_merge(value, action="merge"):
        import netaddr
        if not hasattr(value, "__iter__"):
            raise ValueError("cidr_merge: expected iterable, got " + repr(value))

        if action == "merge":
            try:
                return [str(ip) for ip in netaddr.cidr_merge(value)]
            except Exception as e:
                raise ValueError("cidr_merge: error in netaddr:\n%s" % e)

        elif action == "span":
            # spanning_cidr needs at least two values
            if len(value) == 0:
                return None
            elif len(value) == 1:
                try:
                    return str(netaddr.IPNetwork(value[0]))
                except Exception as e:
                    raise ValueError("cidr_merge: error in netaddr:\n%s" % e)
            else:
                try:
                    return str(netaddr.spanning_cidr(value))
                except Exception as e:
                    raise ValueError("cidr_merge: error in netaddr:\n%s" % e)
        elif action == "collapse":
            networks = list(set([netaddr.IPNetwork(ip) for ip in value]))
            ret = [
                net for net in networks
                if not any(
                    (net != other) and (net.first >= other.first and net.last <= other.last)
                    for other in networks
                )
            ]

            return [str(net_) for net_ in ret]

        else:
            raise ValueError("cidr_merge: invalid action '%s'" % action)

    @staticmethod
    def play_meta(vars: Mapping, **kwargs)-> dict:
        make_cache = kwargs.pop('make_cache', False)
        ts = Helper.ts()

        play_hosts = ','.join(vars.get('ansible_play_hosts_all', []))
        play_batch = ','.join(vars.get('ansible_play_batch', []))
        ret = {
            'ph': 'N/A' if Validate.blank(play_hosts) else play_hosts,
            'if': vars.get('inventory_file', 'N/A'),
            'cf': vars.get('ansible_config_file', 'N/A'),
            'pbd': vars.get('playbook_dir', 'N/A'),
            'pbn': vars.get('ansible_play_name', 'N/A'),
            'pb': 'N/A' if Validate.blank(play_batch) else play_batch,
            'ts': Helper.ts_mod(ts, 'long_safe'), #type: ignore
        }

        kwargs['encoding'] = kwargs.get('encoding', 'utf-8')
        play_id = Str.urlencode(ret, **kwargs)
        play_id = urllib.parse.unquote(play_id, encoding='utf-8', errors='strict')
        ret = {
            'id': {
                'raw': play_id,
                'hash': Str.to_md5(play_id),
            },
            'ts': {
                'raw': ts,
                'str': Helper.ts_mod(ts, 'str'), #type: ignore
                'safe': Helper.ts_mod(ts, 'safe'), #type: ignore
                'long': Helper.ts_mod(ts, 'long'), #type: ignore
                'long_safe': Helper.ts_mod(ts, 'long_safe'), #type: ignore
                'timestamp': Helper.ts_mod(ts, 'timestamp'), #type: ignore
            },
            'placeholder': Helper.placeholder(mod='hash'),
            'cache_file': Helper.path_tmp(f'play_{Str.to_md5(play_id)}.json'),
        }

        if Validate.is_truthy(make_cache) and not Validate.file_exists(ret['cache_file']):
            cache_defaults = kwargs.pop('cache_defaults', {})
            cache_content = Data.combine(cache_defaults, {'play': Helper.copy(ret)}, recursive=True)
            Helper.json_save(cache_content, ret['cache_file'])

        return ret
    
    @staticmethod
    def data_key(*args: str, **kwargs)-> str:
        include_blanks = Validate.truthy(kwargs.pop('blanks', False))
        ret = []
        
        for key in args:
            key = re.sub(r'\.+', '.', key).strip('.')
            if include_blanks or Validate.filled(key):
                ret.append(key)
        
        return '.'.join(ret)
    
    @staticmethod
    def to_toml(data: Mapping, **kwargs)-> str:
        from tomlkit import dumps
        return dumps(data, **kwargs)
    
    @staticmethod
    def from_toml(data: str | bytes)-> dict:
        from tomlkit import parse
        return parse(data)
    
    @staticmethod
    def hash_scrypt(data: str, **kwargs)-> str:
        from passlib.hash import scrypt

        return scrypt.hash(data, **kwargs)
        meta_order = kwargs.pop('meta_order', [])
        kwargs['salt_size'] = kwargs.get('salt_size', scrypt.default_salt_size)
        kwargs['ident'] = kwargs.get('ident', scrypt.default_ident)
        kwargs['parallelism'] = kwargs.get('parallelism', scrypt.parallelism)
        kwargs['block_size'] = kwargs.get('block_size', scrypt.block_size)
        # kwargs['salt_chars'] = kwargs.get('salt_chars', scrypt.default_salt_chars)
        # kwargs['rounds'] = kwargs.get('rounds', scrypt.default_rounds)
        # kwargs['block_size'] = kwargs.get('ident', scrypt.def)
        # kwargs['salt'] = kwargs.get('salt', os.urandom(salt_length))

        
        ret = None
        try:
            ret = scrypt(**kwargs).hash(data)
            # ret = scrypt.hash(data, **kwargs)
        except Exception as e:
            Helper.dump(str(e))
        
        return ret if ret else 'N/A'
        ret = scrypt.hash(data)
        has_salt = 'salt' in kwargs

        if has_salt and kwargs.get('salt', None) is None:
            
            kwargs['salt'] = os.urandom(salt_length)

        ret = scrypt.using(**kwargs).hash(data)
        
        if Validate.filled(meta_order):
            segments = ret.lstrip('$').split('$')
            if not len(segments) >= 3 or segments[0] != 'scrypt' or '=' not in segments[1]:
                raise ValueError('Could not resolve scrypt hash segments to re-order')
            
            meta = {}
            for segment in str(segments[1]).split(','):
                [key, val] = str(segment).split('=', 1)
                meta[str(key)] = str(val)
            
            if not Validate.contains(meta, *meta_order, all=True):
                raise ValueError('Invalid meta_order keys provided')
            
            meta_parts = []
            for key in meta_order:
                val = meta.pop(key)
                meta_parts.append(f'{key}={val}')
            
            if Validate.filled(meta):
                for key, val in meta.items():
                    meta_parts.append(f'{key}={val}')
            
            return '$'.join(['$scrypt', ','.join(meta_parts), '$'.join(segments[2:])])            

        return ret
    
    @staticmethod
    def fs_glob(path: Union[pathlib.Path, str], **kwargs) -> list[pathlib.Path]:
        path = pathlib.Path(path)
        if not path.exists() or not path.is_dir():
            raise ValueError(f'{str(path)} is not a valid directory to glob')
        
        is_recursive = kwargs.pop('recursive', False)
        is_include_files = kwargs.pop('files', True)
        is_include_dirs = kwargs.pop('dirs', True)

        ret = []
        iterate = path.rglob('*') if is_recursive else path.iterdir()
        for item in iterate:
            if (is_include_files and item.is_file()) or (is_include_dirs and item.is_dir()):
                ret.append(item)

        return ret

    @staticmethod
    def fs_get(path: Union[pathlib.Path, str], **kwargs)-> str:
        path = pathlib.Path(path)

        return path.read_text(**kwargs)
    
    @staticmethod
    def normalise_data_key(*args: str) -> str:
        ret = []
        for key in args:
            ret.append(re.sub(r'\.+', '.', key).strip('.'))
        
        return '.'.join(ret)
    
    @staticmethod
    def tap_(value: Any, callback: Callable) -> Any:
        callback(value)
        return value

    @staticmethod
    def with_(value: Any, callback: Callable) -> Any:
        return callback(value)

    @staticmethod
    def fs_lock(file) -> None:
        if sys.platform == 'win32':
            import msvcrt
            saved_pos = file.tell()
            try:
                file.seek(0)
                msvcrt.locking(file.fileno(), msvcrt.LK_LOCK, 1)
            finally:
                file.seek(saved_pos)
        else:
            import fcntl
            fcntl.flock(file.fileno(), fcntl.LOCK_EX)
    
    @staticmethod
    def fs_unlock(file) -> None:
        if sys.platform == 'win32':
            import msvcrt
            saved_pos = file.tell()
            try:
                file.seek(0)
                msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, 1)
            finally:
                file.seek(saved_pos)
        else:
            import fcntl
            fcntl.flock(file.fileno(), fcntl.LOCK_UN)
    
    @staticmethod
    def fs_release(file) -> None:
        Helper.fs_unlock(file)
    
    @staticmethod
    def fs_remove(path: Union[pathlib.Path, str], **kwargs) -> None:
        path = pathlib.Path(path)
        if path.exists():
            if path.is_dir():
                path.rmdir()
            else:
                path.unlink(**kwargs)
    
    @staticmethod
    def fs_delete(path: Union[pathlib.Path, str], **kwargs) -> None:
        Helper.fs_remove(path, **kwargs)
    
    @staticmethod
    def to_md5(data) -> str:
        if Validate.is_mapping(data) or Validate.is_sequence(data):
            data = json.dumps(Helper.to_safe_json(data))

        return hashlib.md5(str(data).encode()).hexdigest()
    
    @staticmethod
    def env_get(key: str, default: Any = None) -> Any:
        return os.environ.get(key, default)

    @staticmethod
    def env_set(key: str, value: str) -> None:
        os.environ[key] = value
    
    @staticmethod
    def env_forget(key: str) -> None:
        if key in os.environ:
            del os.environ[key]

    @staticmethod
    def cache():
        global _CACHE_MODULE
        if _CACHE_MODULE == None:
            from ansible.plugins.cache.memory import CacheModule as CacheModuleMemory
            _CACHE_MODULE = CacheModuleMemory()
        
        return _CACHE_MODULE
    
    @staticmethod
    def to_type_name(data)-> str:
        return type(data).__name__
    
    @staticmethod
    def to_type_module(data)-> str:
        return type(data).__module__
    
    @staticmethod
    def to_type_bases(data)-> list:
        return list(type(data).__bases__)
    
    @staticmethod
    def to_ip_address(data, **kwargs):
        from ansible_collections.ansible.utils.plugins.plugin_utils.base.ipaddress_utils import ip_address
        ph = Helper.placeholder(mod='hashed')
        default = kwargs.get('default', ph)

        try:
            return ip_address(data)
        except Exception as e:
            if default == ph:
                raise e
            
            return default
        
    @staticmethod
    def to_ip_network(data, **kwargs):
        ph = Helper.placeholder(mod='hashed')
        default = kwargs.get('default', ph)

        from ansible_collections.ansible.utils.plugins.plugin_utils.base.ipaddress_utils import ip_network
        try:
            return ip_network(data)
        except Exception as e:
            if default == ph:
                raise e
            
            return default
    
    @staticmethod
    def fs_write(path: pathlib.Path | str, data: str | bytes, **kwargs)-> None:
        path = pathlib.Path(path)
        if Validate.is_string(data):
            path.write_text(str(data), **kwargs)
        else:
            path.write_bytes(data, **kwargs) #type: ignore
    
    @staticmethod
    def fs_read(path: pathlib.Path | str, **kwargs)-> str:
        return pathlib.Path(path).read_text(**kwargs)
    
    @staticmethod
    def json_parse(content: str, **kwargs) -> dict | list:
        return json.loads(content, **kwargs)
    
    @staticmethod
    def yaml_parse(content: str) -> dict | list:
        return yaml.safe_load(content)
    
    @staticmethod
    def json_load(path: pathlib.Path | str, **kwargs) -> dict | list:
        path = pathlib.Path(path)
        if not path.exists():
            raise ValueError(f'Json file [{str(path)}] does not exist.')
        return json.loads(Helper.fs_read(path), **kwargs)

    @staticmethod
    def json_save(content: Mapping | Sequence | str, path: pathlib.Path | str, **kwargs) -> None:
        path = pathlib.Path(path)
        overwrite = kwargs.pop('overwrite', False)

        if path.exists() and not overwrite:
            raise ValueError(f'Json file [{str(path)}] already exists.')
        
        kwargs_path = Data.only_with(kwargs, 'encoding', 'errors')
        kwargs_json = Data.all_except(kwargs, 'encoding', 'errors', 'newline')

        if Validate.is_mapping(content):
            content = json.dumps(Helper.to_safe_json(dict(content)), **kwargs_json) #type: ignore
        elif Validate.is_sequence(content):
            content = json.dumps(Helper.to_safe_json(list(content)), **kwargs_json) #type: ignore
        
        Helper.fs_write(path, str(content), **kwargs_path) #type: ignore

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
    def ts_mod(ts: datetime.datetime, mod: str)-> datetime.datetime | str | int:
        mod = mod.lower()
        match mod:
            case 'string' | 'str':
                return str(ts.strftime("%Y-%m-%dT%H:%M:%SZ"))
            case 'safe':
                return str(ts.strftime("%Y%m%dT%H%M%SZ"))
            case 'long':
                return str(ts.strftime("%Y-%m-%dT%H:%M:%S") + f".{ts.microsecond * 1000:09d}Z")
            case 'long_safe':
                return str(ts.strftime("%Y%m%dT%H%M%S") + f".{ts.microsecond * 1000:09d}Z")
            case 'timestamp':
                return int(ts.timestamp())
            case 'asn1':
                return str(ts.strftime('%Y%m%d%H%M%SZ'))
            case _:
                return ts

    @staticmethod
    def ts(**kwargs):
        ts = datetime.datetime.now(datetime.timezone.utc)
        mod = kwargs.pop('mod', '')
        
        return Helper.ts_mod(ts, mod)
    
    @staticmethod
    def placeholder(*args, **kwargs):
        rand_len = kwargs.pop('rand_len', 32)
        now = Helper.ts()

        ret = str('|'.join([
            ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(math.ceil(rand_len/2))),
            now.strftime("%Y-%m-%dT%H:%M:%S") + f".{now.microsecond * 1000:09d}Z", #type: ignore
            ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(math.floor(rand_len/2)))
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
    
    # @staticmethod
    # def path_relative_to(path: Union[pathlib.Path, str], rel: Union[pathlib.Path, str]) -> str:
    #     path = pathlib.Path(path)
    #     return 

    @staticmethod
    def ensure_directory_exists(path: Union[pathlib.Path, str]) -> None:
        path = pathlib.Path(path)
        path.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def path_tmp(file: str, *args, **kwargs) -> str:
        is_dir = kwargs.pop('dir', False)
        args = list(args)
        ensure_directory_exists = is_dir or len(args) > 1
        args = [tempfile.gettempdir()] + args + [file]
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
    def mapping_to_str(data: Mapping, **kwargs) -> str:
        data = dict(data)
        char_assign = kwargs.pop('assign', '=')
        char_join = kwargs.pop('join', '&')
        as_str = kwargs.pop('as_str', True)
        result = []

        for key, value in data.items():
            if as_str:
                if Validate.is_bool(value):
                    value = 'true' if value else 'false'
                else:
                    value = str(value)
            
            result.append(f'{key}{char_assign}{value}')

        return char_join.join(result).strip(char_join)
    
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
        if Validate.is_bytes(data):
            return Helper.to_safe_json(Helper.to_text(data))
        elif Validate.is_string(data) and Validate.str_is_json(data):
            return Helper.to_safe_json(json.loads(data))
        elif Validate.is_string(data) and Validate.str_is_yaml(data):
            return Helper.to_safe_json(yaml.safe_load(data))
        elif isinstance(data, (str, int, float, bool)) or data is None:
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
        combines = kwargs.pop('combine', [])
        combine_args = kwargs.pop('combine_args', {})
        data_keys = list(data.keys())
        ret = []

        for idx_item in range(0, len(data[data_keys[0]])):
            new_item = defaults.copy()

            if Validate.filled(combines) and Validate.filled(Data.get(combines, str(idx_item))):
                new_item = Data.combine(new_item, Data.get(combines, str(idx_item)), **combine_args)

            for data_key in data_keys:
                if no_dot:
                    new_item[data_key] = data[data_key][idx_item]
                else:
                    Data.set(new_item, data_key, data[data_key][idx_item])

            ret.append(new_item)

        return ret
    
    @staticmethod
    def dirname(path):
        return os.path.dirname(path)

    @staticmethod
    def basename(path):
        return os.path.basename(path)
    
    @staticmethod
    def to_text(*args, **kwargs):
        from ansible.module_utils.common.text.converters import to_text
        strip_quotes = kwargs.pop('strip_quotes', False)

        ret = to_text(*args, **kwargs)
        
        if strip_quotes:
            ret = str(ret).strip().strip("'").strip().strip('"').strip()

        return ret

    @staticmethod
    def to_native(*args, **kwargs):
        return Helper.to_text(*args, **kwargs)

    @staticmethod
    def to_bytes(*args, **kwargs):
        from ansible.module_utils.common.text.converters import to_bytes
        return to_bytes(*args, **kwargs)

    # @staticmethod
    # def from_ansible_tagged_object(data, **kwargs):
    #     if Validate.is_ansible_tagged_object(data):
    #             data = data._native_copy()
        
    #     if Validate.is_mapping(data):
    #         return {str(k): Helper.from_ansible_tagged_object(v) for k, v in data.items()}
    #     elif Validate.is_sequence(data):
    #         return [Helper.from_ansible_tagged_object(item) for item in data]

    #     return data

        # return data._native_copy() if Validate.is_ansible_tagged_object(data) else data

    @staticmethod
    def to_string(data, **kwargs):
        return str(Helper.to_text(data, **kwargs))

    @staticmethod
    def fetch_url_to_module_result(resp, info, **kwargs):
        status_min = int(kwargs.pop('status_min', 200))
        status_max = int(kwargs.pop('status_max', 300))
        status = int(info.get('status', -1))

        ret = {
            'failed': True,
            'msg': '',
            'kwargs': {
                'status': status,
            }
        }
        
        if not (status_min <= status < status_max):
            msg = {'Message': info.get('msg')}

            if Validate.filled(info.get('exception', '')):
                msg['Exception'] = info.get('exception', '')
            
            ret['msg'] = Helper.mapping_to_str(msg, assign=': ', join=' | ')
            
            err_body = None
            if Validate.is_http_response(resp):
                err_body = Helper.to_text(resp.read())
            elif Validate.filled(info.get('body', '')):
                err_body = Helper.to_text(info.get('body', ''))
                
            if Validate.filled(err_body):
                ret['kwargs']['body'] = err_body
        else:
            ret = {
                'failed': False,
                'result': {
                    'status': status,
                    'data': Helper.to_text(resp.read()),
                }
            }
            
            if Validate.str_is_json(ret['result']['data']):
                ret['result']['data'] = json.loads(ret['result']['data'])
        
        return ret

    @staticmethod
    def ansible_open_url_to_result(resp: HTTPResponse, **kwargs):
        status_min = int(kwargs.pop('status_min', 200))
        status_max = int(kwargs.pop('status_max', 300))
        status = int(resp.status)

        ret = {
            'failed': True,
            'msg': '',
            'kwargs': {
                'status': status,
            }
        }
        
        if not (status_min <= status < status_max):
            # msg = {'Message': info.get('msg')}

            # if Validate.filled(info.get('exception', '')):
            #     msg['Exception'] = info.get('exception', '')
            
            # ret['msg'] = Helper.mapping_to_str(msg, assign=': ', join=' | ')
            
            err_body = None
            if Validate.is_http_response(resp):
                err_body = Helper.to_text(resp.read())
                
            if Validate.filled(err_body):
                ret['kwargs']['body'] = err_body
        else:
            ret = {
                'failed': False,
                'result': {
                    'status': status,
                    'data': Helper.to_text(resp.read()),
                }
            }
            
            if Validate.str_is_json(ret['result']['data']):
                ret['result']['data'] = json.loads(ret['result']['data'])
        
        return ret
    
    @staticmethod
    def ip_as_subnet(data: str, **kwargs) -> Any:
        ph = Helper.placeholder(mod='hashed')
        default = kwargs.pop('default', ph)

        if Validate.blank(data):
            return default if default != ph else data

        addr = Helper.ip_as_addr(data)
        proto = 'v4' if Validate.is_ip_v4(addr) else ('v6' if Validate.is_ip_v6(addr) else None)

        if Validate.blank(proto):
            return default if default != ph else data
        
        prefix = str(Str.after_last(data, '/', default=''))
        if Validate.blank(prefix):
            prefix = '32' if proto == 'v4' else '128'

        return f'{addr}/{prefix}'

    @staticmethod
    def ip_as_segments(data: str) -> dict:
        type_ = Helper.ipaddr(data, 'type')
        type_ = 'addr' if type_ == 'address' else ('net' if type_ == 'network' else None)
        
        net = Helper.ipaddr(data, 'network/prefix')
        if net and data == net:
            cidr = net
            addr = Str.before(cidr, '/')
            addr_net = addr
        else:
            cidr = Helper.ipaddr(data, 'address/prefix')
            addr = Helper.ipaddr(data, 'address')
            addr_net = Helper.ipaddr(net, 'address') if net else None

        v4 = Helper.ipaddr(data, 'ipv4')
        v6 = Helper.ipaddr(data, 'ipv6')
        proto = 'v6' if v6 in [data, cidr, addr] else ('v4' if v4 in [data, cidr, addr] else None)

        pub = Helper.ipaddr(addr, 'public') if addr else None
        pri = Helper.ipaddr(addr, 'private') if addr else None

        size_net = Helper.ipaddr(net, 'size') if net else None
        host_cidr = Helper.ipaddr(data, 'host/prefix')
        return {
            'raw': data,
            'type': type_,
            'addr': addr,
            'cidr': cidr,
            'prefix': Helper.ipaddr(data, 'prefix'),
            'proto': proto,
            'ctrl': {
                'v4': proto == 'v4',
                'v6': proto == 'v6',
                'pub': pub in [data, cidr, addr],
                'pri': pri in [data, cidr, addr],
                'valid': Validate.filled(type_) and Validate.filled(proto),
            },
            'net': {
                'addr': addr_net,
                'cidr': net,
                # 'subnet': Helper.ipaddr(net, 'subnet') if net else None,
                'size': size_net,
                'mask': Helper.ipaddr(net, 'netmask') if net else None,
                'broadcast': Helper.ipaddr(net, 'broadcast') if net else None,
            },
            'host': {
                'addr': Helper.ipaddr(host_cidr, 'address') if host_cidr else None,
                'cidr': host_cidr,
            },
            'wrap': {
                'addr': Helper.ipaddr(addr, 'wrap') if addr else None,
                'cidr': Helper.ipaddr(cidr, 'wrap') if cidr else None,
            },
            'first': {
                'addr': Helper.ipaddr(Helper.ipaddr(net, '1'), 'address') if net else None,
                'cidr': Helper.ipaddr(net, '1') if net else None,
                'usable': Helper.ipaddr(net, 'first_usable') if net else None,
            },
            'last': {
                'addr': Helper.ipaddr(Helper.ipaddr(net, '-1'), 'address') if net else None,
                'cidr': Helper.ipaddr(net, '-1') if net else None,
                'usable': Helper.ipaddr(net, 'last_usable') if net else None,
            },
            'range': {
                'usable': str(Helper.ipaddr(net, 'range_usable')).split('-', 2) if net and size_net and size_net > 1 else None,
            }
        }
    
    @staticmethod
    def ip_as_addr(data: str, **kwargs) -> str:
        ph = Helper.placeholder(mod='hashed')
        default = kwargs.pop('default', ph)
        
        addr = Str.before(data, '/')
        proto = 'v4' if Validate.is_ip_v4(addr) else ('v6' if Validate.is_ip_v6(addr) else None)

        if Validate.blank(proto):
            return default if default != ph else data
                
        from_network = kwargs.pop('from_network', True)

        if not Validate.is_falsy(from_network):
            if Validate.is_ip_v4(addr) and Str.after_last(addr, '.') == '0':
                return Str.before_last(addr, '.') + '.1'
            elif Validate.is_ip_v6(addr):
                if addr.endswith('::'):
                    return Str.before_last(addr, '::') + '::1'
                elif addr.endswith('::0'):
                    return Str.before_last(addr, '::0') + '::1'
                elif addr.endswith(':0'):
                    return Str.before_last(addr, ':0') + ':1'
                elif addr.endswith(':'):
                    return Str.before_last(addr, ':') + ':1'
        
        return addr
    
    @staticmethod
    def subnets_collapse(data, **kwargs) -> list:
        ret = []
        only = kwargs.pop('only', '')
        only_private = only in ['pri', 'private']
        only_public = only in ['pub', 'public']

        proto = kwargs.pop('proto', '')
        only_v4 = proto in ['4', 'v4', 4]
        only_v6 = proto in ['6', 'v6', 6]

        for subnet in data:
            addr = Helper.ip_as_addr(subnet)
            
            if (only_private and Validate.is_ip_public(addr)) or (only_public and Validate.is_ip_private(addr)):
                continue

            if (only_v4 and Validate.is_ip_v6(addr)) or (only_v6 and Validate.is_ip_v4(addr)):
                continue

            supernets = list(set(data) - set([subnet]))
            if not any([Validate.is_subnet_of(subnet, supernet) for supernet in supernets]):
                ret.append(subnet)

        return list(set(ret))
    
    @staticmethod
    def to_lua(data: Mapping | Sequence) -> str:
        import luadata
        
        return luadata.serialize(Helper.to_safe_json(data))

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

class Str:
    @staticmethod
    def pad(data: Any, count: int = 4, char: str = ' ', **kwargs) -> str:
        padding = kwargs.pop('pad')
        if padding not in ['left', 'right', 'both']:
            raise ValueError(f'Invalid padding type [{padding}]. Available: left, right, both')

        count = max([count, 0])
        data = str(Helper.to_text(data))
        is_strip = kwargs.pop('strip', True)
        is_dent = kwargs.pop('dent', False)

        if not Validate.is_falsy(is_strip):
            data = data.strip()
                
        if Validate.is_truthy(is_dent):
            padding = 'left' if padding == 'right' else ('right' if padding == 'left' else padding)
            count += len(data)
        
        if padding == 'left':
            return str(data).ljust(count, char)
        elif padding == 'right':
            return str(data).rjust(count, char)
        else:
            return str(data).center(count, char)

    @staticmethod
    def ljust(data: Any, count: int = 4, char: str = ' ', **kwargs) -> str:
        kwargs['pad'] = 'left'
        return Str.pad(data, count, char, **kwargs)

    @staticmethod
    def rjust(data: Any, count: int = 4, char: str = ' ', **kwargs) -> str:
        kwargs['pad'] = 'right'
        return Str.pad(data, count, char, **kwargs)

    @staticmethod
    def center(data: Any, count: int = 4, char: str = ' ', **kwargs) -> str:
        kwargs['pad'] = 'both'
        return Str.pad(data, count, char, **kwargs)
    
    @staticmethod
    def pad_left(data: Any, count: int = 4, char: str = ' ', **kwargs) -> str:
        return Str.ljust(data, count, char, **kwargs)

    @staticmethod
    def pad_right(data: Any, count: int = 4, char: str = ' ', **kwargs) -> str:
        return Str.rjust(data, count, char, **kwargs)

    @staticmethod
    def pad_both(data: Any, count: int = 4, char: str = ' ', **kwargs) -> str:
        return Str.rjust(data, count, char, **kwargs)
    
    @staticmethod
    def remove_empty_lines(data: str) -> str:
        return re.sub(r'(\n\s*){2,}', '\n', re.sub(r'^\s*[\r\n]+|[\r\n]+\s*\Z', '', data))
    
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
    def find(haystack, needle, reverse = False, before = True, **kwargs) -> str:
        ph = Helper.placeholder(mod='hashed')
        default = str(kwargs.pop('default', ph))

        index = haystack.rfind(needle) if reverse else haystack.find(needle)
        ret = str(haystack if index == -1 else (haystack[:index] if before else haystack[index + len(needle):]))
        return default if default != ph and ret == haystack else ret
    
    @staticmethod
    def before(haystack, needle, **kwargs) -> str:
        return Str.find(haystack, needle, **kwargs)
    
    @staticmethod
    def before_last(haystack, needle, **kwargs) -> str:
        return Str.find(haystack, needle, reverse = True, **kwargs)
    
    @staticmethod
    def after(haystack, needle, **kwargs) -> str:
        return Str.find(haystack, needle, reverse = False, before = False, **kwargs)
    
    @staticmethod
    def after_last(haystack, needle, **kwargs) -> str:
        return Str.find(haystack, needle, reverse = True, before = False, **kwargs)
    
    @staticmethod
    def start(haystack, needle) -> str:
        if Validate.is_string(needle) and Validate.filled(needle) and not str(haystack).startswith(needle):
            return needle + haystack
        
        return haystack
    
    @staticmethod
    def finish(haystack, needle) -> str:
        if Validate.is_string(needle) and Validate.filled(needle) and not str(haystack).endswith(needle):
            return haystack + needle
        
        return haystack
    
    @staticmethod
    def wrap(data, start, finish = None) -> str:
        finish = finish if Validate.is_string(finish) else start
        
        return Str.finish(Str.start(data, start), finish)
    
    @staticmethod
    def case_snake(data) -> str:
        import re
        s = re.sub(r'([A-Z][a-z]+)', r' \1',
                    re.sub(r'([A-Z]+)', r' \1',
                            data.replace('-', ' ')))
        return '_'.join(s.split()).lower()
    
    @staticmethod
    def to_md5(data) -> str:
        return Helper.to_md5(data)
    
    @staticmethod
    def url_strip(data):
        return re.sub(r'^https?://', '', str(data))
    
    @staticmethod
    def urlencode(data, **kwargs)-> str:
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
    def hmac_compare(hash_a, hash_b)-> bool:
        import hmac
        
        return hmac.compare_digest(hash_a, hash_b)
    
    @staticmethod
    def is_host_matches_host_hash(hmac_key: str, hmac_hash: str, *args: str)-> bool:
        import hmac
        
        for host in args:
            computed_hash = hmac.new(base64.b64decode(hmac_key), Helper.to_bytes(host), hashlib.sha1).digest() #type: ignore
            if hmac.compare_digest(computed_hash, base64.b64decode(hmac_hash)):
                return True
        
        return False
    
    @staticmethod
    def is_item_exec(data: Mapping)-> bool:
        return not Validate.is_truthy(Data.get('_skip', False)) and not Validate.is_falsy(Data.get('_keep', True))
    
    @staticmethod
    def is_plugin_lookup(data)-> bool:
        if Validate.blank(data) or not Validate.is_object(data):
            return False
        
        mros = type(data).__mro__

        return Data.get(mros, '0.__name__') == 'LookupModule' and Data.get(mros, '1.__name__') == 'LookupBase' and Data.get(mros, '1.__module__') == 'ansible.plugins.lookup'
    
    @staticmethod
    def is_plugin_action(data)-> bool:
        if Validate.blank(data) or not Validate.is_object(data):
            return False
        
        mros = type(data).__mro__

        return Data.get(mros, '0.__name__') == 'ActionModule' and Data.get(mros, '1.__name__') == 'ActionBase' and Data.get(mros, '1.__module__') == 'ansible.plugins.action'
    
    @staticmethod
    def has_method(obj, method: str)-> bool:
        return Validate.filled(obj) and Validate.filled(method) and hasattr(obj, method) and callable(getattr(obj, method))
        
    @staticmethod
    def is_copyable(data):
        try:
            copy.copy(data)
            return True
        except Exception:
            return False
    
    @staticmethod
    def is_deepcopyable(data):
        try:
            copy.deepcopy(data)
            return True
        except Exception:
            return False
    
    @staticmethod
    def str_endswith(haystack: str, *args, **kwargs)-> bool:
        for needle in args:
            res = haystack.endswith(needle, **kwargs)
            if res:
                return True
        
        return False
    
    @staticmethod
    def str_startswith(haystack: str, *args, **kwargs)-> bool:
        for needle in args:
            res = haystack.startswith(needle, **kwargs)
            if res:
                return True
        
        return False
    
    @staticmethod
    def str_ansible_vault(haystack: str)-> bool:        
        return haystack.strip().startswith('$ANSIBLE_VAULT;')

    @staticmethod
    def str_contains(haystack: str, *args, **kwargs)-> bool:
        for needle in args:
            res = needle in haystack
            if res:
                return True
        
        return False

    @staticmethod
    def is_fs_locked(file):
        try:
            if sys.platform == 'win32':
                import msvcrt
                saved_pos = file.tell()
                try:
                    file.seek(0)
                    msvcrt.locking(file.fileno(), msvcrt.LK_NBRLCK, 1)
                except OSError as e:
                    if e.errno == errno.EACCES:
                        return True
                    raise
                finally:
                    file.seek(saved_pos)
                
                file.seek(0)
                msvcrt.locking(file.fileno(), msvcrt.LK_UNLCK, 1)
                file.seek(saved_pos)
            else:
                import fcntl
                fcntl.flock(file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                fcntl.flock(file.fileno(), fcntl.LOCK_UN)
            return False
        except OSError as e:
            if sys.platform != 'win32' and e.errno in (errno.EAGAIN, errno.EWOULDBLOCK):
                return True
            raise

    @staticmethod
    def is_truthy(data)-> bool:
        return Helper.to_string(data).lower() in ('y', 'yes', 'on', '1', 'true', 't', 1, 1.0)
    
    @staticmethod
    def truthy(data)-> bool:
        return Validate.is_truthy(data)
    
    @staticmethod
    def is_falsy(data)-> bool:
        return Helper.to_string(data).lower() in ('n', 'no', 'off', '0', 'false', 'f', 0, 0.0)
    
    @staticmethod
    def falsy(data)-> bool:
        return Validate.is_falsy(data)
    
    @staticmethod
    def is_exception(data)-> bool:
        return isinstance(data, BaseException) or (isinstance(data, type) and issubclass(data, BaseException))
    
    @staticmethod
    def is_ip(data)-> bool:
        return Helper.to_ip_address(data, default=False) != False
    
    @staticmethod
    def is_network(data)-> bool:
        return Helper.to_ip_network(data, default=False) != False
    
    @staticmethod
    def is_ip_v4(data)-> bool:
        return Helper.to_ip_address(data).version == 4 #type: ignore
    
    @staticmethod
    def is_ip_v6(data)-> bool:
        return Helper.to_ip_address(data).version == 6 #type: ignore
    
    @staticmethod
    def is_ip_public(data)-> bool:        
        return Helper.to_ip_address(data).is_global #type: ignore
    
    @staticmethod
    def is_ip_private(data)-> bool:
        return Helper.to_ip_address(data).is_private #type: ignore
    
    @staticmethod
    def is_subnet_of(network_a, network_b)-> bool:
        network_a = Helper.to_ip_network(network_a)
        network_b = Helper.to_ip_network(network_b)
        
        if Validate.is_exception(network_a) or Validate.is_exception(network_b):
            return False
        
        try:
            if network_a._version != network_b._version: #type: ignore
                return False
            return (
                network_b.network_address <= network_a.network_address #type: ignore
                and network_b.broadcast_address >= network_a.broadcast_address #type: ignore
            )
        except Exception:
            return False
    
    @staticmethod
    def is_supernet_of(network_a, network_b)-> bool:
        return Validate.is_subnet_of(network_b, network_a)
    
    @staticmethod
    def is_http_error(data):
        import urllib.error
        return Validate.is_object(data) and isinstance(data, urllib.error.HTTPError)

    @staticmethod
    def is_http_response(data):
        import http.client
        return Validate.is_object(data) and isinstance(data, http.client.HTTPResponse)
    
    @staticmethod
    def is_int_even(data: int) -> bool:
        return data % 2 == 0
    
    @staticmethod
    def is_int_odd(data: int) -> bool:
        return not Validate.is_int_even(data)
    
    @staticmethod
    def is_env_ansible():
        return any(mod in sys.modules for mod in _DEFAULTS_TOOLS['validate']['ansible']['entrypoints'])

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
    def is_iterable(data) -> bool:
        return isinstance(data, Iterable)
    
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
    def is_python_native(data):
        return type(data).__module__ == 'builtins'
    
    @staticmethod
    def is_ansible_mapping(data):
        return Validate.is_hostvars(data) or Validate.is_hostvarsvars(data) or Validate.is_lazytemplatedict(data)
    
    @staticmethod
    def is_ansible_marker(data):
        return Validate.is_object(data) and type(data).__module__ == 'ansible._internal._templating._jinja_common' and type(data).__name__ == 'Marker'

    @staticmethod
    def is_ansible_undefined_marker(data):
        return Validate.is_object(data) and type(data).__module__ == 'ansible._internal._templating._jinja_common' and type(data).__name__ == 'UndefinedMarker'
    
    @staticmethod
    def is_ansible_tagged_object(data):
        return Validate.is_object(data) and type(data).__module__ == 'ansible.module_utils._internal._datatag' and any("AnsibleTaggedObject" == cls.__name__ for cls in type(data).__mro__)
    
    @staticmethod
    def is_ansible_tagged_data(data):
        return Validate.is_object(data) and type(data).__module__ == 'ansible.module_utils._internal._datatag'

    @staticmethod
    def is_ansible_tagged_date(data):
        return Validate.is_ansible_tagged_data(data) and type(data).__name__ == '_AnsibleTaggedDate'

    @staticmethod
    def is_ansible_tagged_time(data):
        return Validate.is_ansible_tagged_data(data) and type(data).__name__ == '_AnsibleTaggedTime'

    @staticmethod
    def is_ansible_tagged_datetime(data):
        return Validate.is_ansible_tagged_data(data) and type(data).__name__ == '_AnsibleTaggedDateTime'

    @staticmethod
    def is_ansible_tagged_str(data):
        return Validate.is_ansible_tagged_data(data) and type(data).__name__ == '_AnsibleTaggedStr'
    
    @staticmethod
    def is_ansible_tagged_int(data):
        return Validate.is_ansible_tagged_data(data) and type(data).__name__ == '_AnsibleTaggedInt'
    
    @staticmethod
    def is_ansible_tagged_float(data):
        return Validate.is_ansible_tagged_data(data) and type(data).__name__ == '_AnsibleTaggedFloat'
    
    @staticmethod
    def is_ansible_tagged_list(data):
        return Validate.is_ansible_tagged_data(data) and type(data).__name__ == '_AnsibleTaggedList'
    
    @staticmethod
    def is_ansible_tagged_set(data):
        return Validate.is_ansible_tagged_data(data) and type(data).__name__ == '_AnsibleTaggedSet'
    
    @staticmethod
    def is_ansible_tagged_tuple(data):
        return Validate.is_ansible_tagged_data(data) and type(data).__name__ == '_AnsibleTaggedTuple'

    @staticmethod
    def is_ansible_tagged_dict(data):
        return Validate.is_ansible_tagged_data(data) and type(data).__name__ == '_AnsibleTaggedDict'
    
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
    def is_sequence_of_mappings(data):
        return Validate.is_sequence(data) and all(Validate.is_ansible_mapping(item) for item in data)
    
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
    def _is_blank(data):
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
    def _is_filled(data):
        return not Validate._is_blank(data)
    
    @staticmethod
    def is_type_name(data, type_):
        type_ = Helper.to_iterable(type_)

        if Helper.to_type_name(data) in type_:
            return True
        
        return any([Validate.is_type_of(data, entry) for entry in type_])
    
    @staticmethod
    def blank(data, **kwargs):
        ret = Validate._is_blank(data)
        type_ = kwargs.get('type', None)
        
        if ret and not Validate._is_blank(type_):
            ret = Validate.is_type_name(data, type_)
    
        return ret
    
    @staticmethod
    def filled(data, **kwargs):
        ret = Validate._is_filled(data)
        type_ = kwargs.get('type', None)
        
        if ret and not Validate._is_blank(type_):
            ret = Validate.is_type_name(data, type_)
    
        return ret
    
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
            case 'str' | 'string':
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
            case 'sequence':
                return Validate.is_sequence(data)
            case 'mapping':
                return Validate.is_mapping(data)
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
    def is_file(path):
        return os.path.isfile(path)
    
    @staticmethod
    def is_file_readable(path: Union[pathlib.Path, str]) -> bool:
        path = pathlib.Path(path)
        if not path.exists() or not path.is_file():
            return False

        return os.access(path, os.R_OK)
    
    @staticmethod
    def is_file_writable(path: Union[pathlib.Path, str]) -> bool:
        path = pathlib.Path(path)
        if not path.exists() or not path.is_file():
            return False
        
        return os.access(path, os.W_OK)
    
    @staticmethod
    def is_dir(path):
        return os.path.isdir(path)
    
    @staticmethod
    def is_dir_readable(path: Union[pathlib.Path, str]) -> bool:
        path = pathlib.Path(path)
        if not path.exists() or not path.is_dir():
            return False

        return os.access(path, os.R_OK)
    
    @staticmethod
    def is_dir_writable(path: Union[pathlib.Path, str]) -> bool:
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
    def str_is_regex(haystack: str, patterns: Sequence, *args, **kwargs):
        import re
        is_cli = kwargs.get('cli', False)
        is_all = kwargs.get('all', False)
        is_escape = kwargs.get('escape', False)
        is_prepare = kwargs.get('prepare', False)
        
        patterns = list(patterns)
        if is_cli and Validate.is_string(patterns):
            patterns = Str.to_cli(patterns)
        
        if Validate.blank(patterns):
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
                    myvars.append(Helper.to_text(x))
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
    
    def _validate_ip(self, constraint, field, value):
        """{'type': 'boolean'}"""
        if constraint is True and not Validate.is_ip(value):
            self._error(field, f"[{value}] Must be an IP address") #type: ignore
        elif constraint is False and Validate.is_ip(value):
            self._error(field, f"[{value}] cannot be an IP address") #type: ignore
    
    def _validate_ipv4(self, constraint, field, value):
        """{'type': 'boolean'}"""
        if constraint is True and not Validate.is_ip_v4(value):
            self._error(field, f"[{value}] Must be an IPv4 address") #type: ignore
        elif constraint is False and Validate.is_ip_v4(value):
            self._error(field, f"[{value}] cannot be an IPv4 address") #type: ignore
    
    def _validate_ipv6(self, constraint, field, value):
        """{'type': 'boolean'}"""
        if constraint is True and not Validate.is_ip_v4(value):
            self._error(field, f"[{value}] Must be an IPv6 address") #type: ignore
        elif constraint is False and Validate.is_ip_v4(value):
            self._error(field, f"[{value}] cannot be an IPv6 address") #type: ignore
    
    def _validate_unique_field(self, constraint, field, value):
        """ {'type': ['string', 'list']} """

        errors = {}
        for unique_field in Helper.to_iterable(constraint):
            # Build hash set for uniqueness check
            hashes = []
            for channel in value:
                if unique_field not in channel:
                    continue  # Skip if field is missing (handles optional fields from oneof/anyof)
                field_value = channel[unique_field]
                if isinstance(field_value, dict):
                    h = hash(frozenset(field_value.items()))
                elif isinstance(field_value, list):
                    # For lists, sort and tuple to make hashable (assuming elements are hashable)
                    h = hash(tuple(sorted(field_value)))
                else:
                    h = hash(field_value)
                hashes.append((h, field_value))  # Store value for error reporting

            # Detect and log duplicates
            seen = {}
            for i, (h, field_value) in enumerate(hashes):
                if h in seen:
                    prev_i = seen[h]
                    # Error on the current (duplicate) item
                    if str(i) not in errors:
                        errors[str(i)] = {}
                    errors[str(i)][unique_field] = f"value '{field_value}' duplicates previous at index {prev_i}"
                else:
                    seen[h] = i

        # Report errors if any
        if errors:
            self._error(field, errors)

    def error_message(self) -> str:
        parts = []
        for key_name, error in (Data.dot(self.errors)).items(): #type: ignore
            parts.append(f'{key_name}: {error}')
        
        return ' | '.join(parts)

class Fluent():
    on_save: Optional[Callable] = None
    on_destroy: Optional[Callable] = None

    def __init__(self, data: Mapping[Any, Any] = {}):
        self.data = dict(data).copy()
    
    def get(self, key: str, default: Any = None)-> Any:
        return Data.pydash().get(self.data, key, default)
    
    def get_filled(self, key: str, default, **kwargs)-> Any:
        if not self.has(key):
            return default
        
        ret = self.get(key)
        return default if not Validate.filled(ret, **kwargs) else ret
    
    def set(self, key: str, value: Any)-> dict:
        Data.pydash().set_(self.data, key, value)
        return self.data
    
    def increase(self, key: str, start: int|float = 0, step: int|float = 1)-> int | float:
        current = self.get(key, start)
        current += step
        self.set(key, current)
        return current
    
    def decrease(self, key: str, start: int|float = 0, step: int|float = 1)-> int | float:
        current = self.get(key, start)
        current -= step
        self.set(key, current)
        return current
    
    def forget(self, key: str)-> dict:
        Data.pydash().unset(self.data, key)
        return self.data
    
    def unset(self, key: str)-> dict:
        return self.forget(key)

    def has(self, key: str)-> bool:
        return Data.pydash().has(self.data, key)

    def filled(self, key: str)-> bool:
        return Validate.filled(self.get(key))
    
    def contains(self, key: str, *args, **kwargs)-> bool:
        return Validate.contains(self.get(key, []), *args, **kwargs)

    def blank(self, key: str)-> bool:
        return Validate.blank(self.get(key))
    
    def append(self, key: str, value, **kwargs)-> dict:
        self.data = dict(Data.append(self.data, key, value, **kwargs))
        return self.data

    def prepend(self, key: str, value, **kwargs)-> dict:
        self.data = dict(Data.prepend(self.data, key, value, **kwargs))
        return self.data

    def all(self)-> dict:
        return self.data.copy()

    def only_with(self, *args, **kwargs):
        return Data.only_with(self.all(), *args, **kwargs)
    
    def all_except(self, *args, **kwargs):
        return Data.all_except(self.all(), *args, **kwargs)
    
    def pydash(self):
        return Data.pydash()
    
    def copy(self):
        return Fluent(self.all())
    
    def __copy__(self):
        return self.copy()

    def __deepcopy__(self):
        return self.copy()
    
    def save(self)-> None:
        if Validate.blank(self.on_save):
            return
        
        Helper.callback(self.on_save, self.all())

class Cache:
    @staticmethod
    def make(file_name_prefix: str = ''):
        file_name = f'{file_name_prefix}{Helper.placeholder(mod='hashed')}.json'
        file_path = Helper.path_tmp(file_name)
        
        if not Validate.file_exists(file_path):
            Helper.json_save({'ts': Helper.ts(mod='long')}, file_path)
        
        return file_path

    @staticmethod
    def load(file_path: str)-> Fluent:
        if not Validate.file_exists(file_path):
            raise ValueError(f'Cache file [{file_path}] does not exit.')
        
        cache = Fluent(dict(Helper.json_load(file_path)))
        cache.on_save = lambda data: Helper.json_save(data, file_path, overwrite=True)

        return cache

class Aggregator:
    DataQuery = DataQuery
    Data = Data
    Helper = Helper
    Str = Str
    Validate = Validate
    Validator = Validator
    Cache = Cache
    Fluent = Fluent