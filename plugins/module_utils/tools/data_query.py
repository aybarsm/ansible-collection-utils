from __future__ import annotations
import re
from collections.abc import Mapping
from ansible_collections.aybarsm.utils.plugins.module_utils.tools import Helper, Jinja, Data, Validate

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