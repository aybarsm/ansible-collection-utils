import typing as t
import re
from jinja2.runtime import Context
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    _CONF, __ansible, __convert, __data, __factory, __str, __utils, __validate
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.fluent import Fluent

Ansible = __ansible()
Convert = __convert()
Data = __data()
Factory = __factory()
Str = __str()
Utils = __utils()
Validate = __validate()

class DataQuery:
    def __init__(
        self,
        context: t.Optional[Context] = None,
        data: t.Sequence[t.Any] = [],
        query: str = '',
        *bindings: t.Any,
        **kwargs: t.Any,
    ):
        self.cfg: Fluent = Fluent(_CONF['data_query'])
        self.context: t.Optional[Context] = None
        self.data: list[t.Any] = []
        self.query: str = ''
        self.bindings_positional: list[t.Any] = []
        self.bindings_named: dict[str, t.Any] = {}
        self.operators_and: list[str] = []
        self.operators_or: list[str] = []
        self.tokens: Fluent = Fluent()

        self.set_context(context)
        self.set_data(data)

        bindings_named = {}
        for key_, val_ in kwargs.items():
            key_ = str(key_)
            if key_.startswith('_'):
                self.cfg.set(f'settings.{key_.strip('_')}', val_)
            else:
                bindings_named[key_.strip(':')] = val_
        
        self.set_query(
            query, 
            list(bindings), 
            bindings_named,
            self.cfg.get('settings.operators_and', ['and', 'AND', '&&']),
            self.cfg.get('settings.operators_or', ['or', 'OR', '||']),
        )
    
    def resolve_tokens(self):
        self.tokens = Fluent()
        master = {'idx': 0, 'next': 1}
        stack = []

        segments = self.get_query_segments()
        for idx, segment in enumerate(segments):
            stack_key = self.tokens.get('_meta.stack.key')
            if (self.is_token_segment_operator(segment) or segment in ['(', ')']) and self.should_token_batch_finalise():
                self._token_batch_finalise(stack_key)

            if segment == '(':
                if idx == 0:
                    stack = [master]
                else:
                    if len(stack) == 1 and stack[0]['idx'] == 0:
                        stack = []
                        parent = master
                    else:
                        parent = stack[-1]
                    
                    stack.append({'idx': parent['next'], 'next': 0})
                    parent['next'] += 1
            elif segment == ')':
                stack.pop()
                
                if Validate.blank(stack):
                    stack.append(master)
            
            if segment in ['(', ')']:
                key_segments = [str(n['idx']) for n in stack]
                
                if len(key_segments) > 1:
                    key_segments = [key_segments[0]] + Data.flatten(Utils.product(['subs'], key_segments[1:]))

                self.tokens.set('_meta.stack.key', '.'.join(key_segments))
                # self.tokens.set('_meta.stack.key', '_'.join(str(n['idx']) for n in stack))
                continue
            
            if self.is_token_segment_operator(segment):
                if not self.tokens.has(f'{stack_key}.cond'):
                    self.tokens.set(
                        f'{stack_key}.cond',
                        ('all' if self.is_token_segment_operator_and(segment) else 'any')
                    )
                    self.tokens.set(
                        f'{stack_key}.key',
                        stack_key
                    )
                
                continue

            self._resolve_token_segment(segment)
        
        if not self.tokens.has('0.cond'):
            self.tokens.set('0.cond', 'any')
    
    def _token_batch_finalise(self, stack_key: str) -> None:
        self.tokens.append(
            f'{stack_key}.tests',
            self._resolve_token_test_batch()
        )
        
        self.tokens.set('_meta.batch', {})

    def _resolve_token_segment(self, segment: str) -> None:
        item = self._resolve_token_segment_item(segment)
        
        if not self.is_token_segment_item_extra_args(item):
           self.tokens.append('_meta.batch.args', item)
           return
        
        qs_ = Convert.from_qs(Str.chop_both(item, '`'), keep_blank_values=True)
        for key_, val_ in qs_.items():
            val_ = Data.first(Convert.to_iterable(val_))
            if self.is_token_segment_item_binding(key_) and Validate.filled(val_):
                raise ValueError('Extra arguments bound to bindings cannot have value.')
            
            key_item = self._resolve_token_segment_item(key_)
            if Validate.blank(val_):
                self.tokens.append('_meta.batch.args', key_item)
                continue

            self.tokens.set(
                f'_meta.batch.kwargs.{key_item}', 
                self._resolve_token_segment_item(val_)
            )

    def _resolve_token_segment_item(self, segment: str) -> t.Any:
        if self.is_token_segment_item_binding_positional(segment):
            ret = self.bindings_positional[self.cfg.get('b_pos', 0)]
            self.cfg.increase('b_pos')
        elif self.is_token_segment_item_binding_named(segment):
            ret = self.bindings_named[segment.lstrip(':')]
        else:
           ret = segment
        
        return ret
    
    def _resolve_token_test_batch(self) -> dict:
        ret = {
            'negate': False,
            'args': list(self.tokens.get('_meta.batch.args', [])),
            'kwargs': dict(self.tokens.get('_meta.batch.kwargs', {})),
        }

        if not self.is_mod_attr():
            ret['args'].insert(0, 'value')
        else:
            ret['args'][0] = Convert.to_data_key('value', ret['args'][0])
        
        if self.is_mod_attr():
            self.tokens.append('_meta.data_keys', ret['args'][0], unique=True)
        
        if len(ret['args']) < 2:
            raise ValueError(f'Test not found in query syntax: {Convert.to_text(ret)}')

        if ret['args'][1] == 'not':
            ret['negate'] = True
            ret['args'] = [arg_ for idx_, arg_ in enumerate(ret['args']) if idx_ != 1]
        
        ret['args'][1] = self._resolve_token_test_fqn(ret['args'][1])
            
        return ret
    
    def _resolve_token_test_fqn(self, test: str) -> str:
        if '.' not in test:
            return Convert.to_data_key('ansible.builtin.', test)
        else:
            for prefix, namespace in dict(self.cfg.get('test.prefixes', {})).items():
                if test.startswith(prefix):
                    test = Convert.to_data_key(namespace, Str.chop_start(test, prefix))
                    break

        if test.count('.') != 2:
            raise ValueError(f'Invalid test fqn [{test}]')
        
        return test
    
    def set_context(self, context: t.Optional[Context]) -> None:
        self.context = context
    
    def set_data(self, data: t.Sequence[t.Any]) -> None:
        self.data = list(data)
    
    def set_query(
        self, 
        query: str,
        bindings_positional: list[t.Any] = [],
        bindings_named: dict[str, t.Any] = {},
        operators_and: list[str] = [], 
        operators_or: list[str] = []
    ) -> None:
        self.__set_operators(operators_and, operators_or)
        query = query.strip()
        
        if query.count('(') != query.count(')'):
            raise ValueError('Invalid query syntax: Number of parentheses not matching.')

        if not Validate.is_int_even(query.count('`')):
            raise ValueError('Invalid query syntax: Number of backticks not even.')
        
        pattern_operators = re.compile(rf'\\s+({'|'.join([re.escape(oper) for oper in self.operators_and + operators_or])})\\s+')
        pattern_query_parenthese = re.compile(r'\\(\\s*([a-z][a-z0-9_.]*\\s+[a-z][a-z0-9_.]*(?:\\s+(?:\\?|\\:[a-z][a-z0-9_]*))?)\\s*\\)')
        bindings_named = Data.combine(self.cfg.get('defaults.bindings.named', {}), bindings_named)

        query = re.sub(r'\)', ') ', query)
        query = re.sub(r'\(', '( ', query)
        query = re.sub(r'\(([A-Za-z0-9])', '( \\1', query)
        query = re.sub(r'([A-Za-z0-9?])\)', '\\1 )', query)
        query = re.sub(r'\:+([A-Za-z0-9_]+?)', ':\\1', query)
        query = re.sub(r'\`+', '`', query)
        query = pattern_operators.sub(r' \1 ', query)
        query = re.sub(r'\s+', r' ', query.strip())
        
        while True:
            new_query = pattern_query_parenthese.sub(r'\1', query)
            if new_query == query:
                break
            query = new_query
        
        query = '( ' + query + ' )'

        if query.count('?') != len(bindings_positional):
            raise ValueError('Invalid number of positional bindings')
        
        b_named = list(set(re.findall(r'[\(+|\s]?:+([A-Za-z0-9_]+)[\)+|\s]?', query)))
        
        if not Validate.contains(bindings_named, *b_named, all = True):
            raise ValueError('Missing named bindings')
        
        self.query = query
        self.bindings_positional = bindings_positional
        self.bindings_named = bindings_named
        self.resolve_tokens()
    
    def __set_operators(self, operators_and: list[str] = [], operators_or: list[str] = []) -> None:
        opposites_ = {'and': 'or', 'or': 'and'}
        for type_, operators in {'and': operators_and, 'or': operators_or}.items():
            if Validate.blank(operators):
                continue

            opposite_ = opposites_[type_]
            intersect = Data.intersect(operators, getattr(self, f'operators_{opposite_}'))
            if Validate.filled(intersect):
                raise ValueError(f'{type_.upper()} operators [{', '.join(intersect)}] already exist as `{opposite_.upper()}` operators.')
            
            current = getattr(self, f'operators_{type_}')
            if Validate.filled(Data.difference(operators, current)):
                setattr(self, f'operators_{type_}', operators)
    
    def get_query_segments(self) -> list:
        return self.query.split(' ')

    def get_tokens(self) -> dict:
        ret = self.tokens.all()
        
        if '_meta' in ret:
            del ret['_meta']
        
        return dict(sorted(ret.items()))
    
    def get_token_masters(self, exclude_main: bool = False) -> list:
        return list(sorted([key_ for key_ in self.tokens.keys() if '_' not in str(key_) and (not exclude_main or str(key_) != '0')]))
    
    def get_tokens_data_keys(self) -> list:
        return self.tokens.get('_meta.data_keys')
    
    def get_default_return(self) -> t.Any:
        if self.cfg.get('settings.default'):
            return self.cfg.get('settings.default')
        elif self.is_mod_attr() and self.is_first_result():
            return {}
        else:
            return []
    
    def get_tokens_master_condition(self) -> str:
        return self.tokens.get('0.cond')
    
    def is_first_result(self) -> bool:
        return self.cfg.get('settings.first') == True
    
    def is_mode_debug(self) -> bool:
        return self.cfg.get('settings.debug') == True
    
    def is_mod_attr(self) -> bool:
        return Validate.is_enumeratable_of_mappings(self.data)
    
    def is_token_segment_operator_and(self, segment: str) -> bool:
        return segment in self.operators_and
    
    def is_token_segment_operator_or(self, segment: str) -> bool:
        return segment in self.operators_or

    def is_token_segment_operator(self, segment: str) -> bool:
        return self.is_token_segment_operator_and(segment) or self.is_token_segment_operator_or(segment)
    
    def has_token_batch_args(self) -> bool:
        return self.tokens.filled('_meta.batch.args')
    
    def has_token_batch_kwargs(self) -> bool:
        return self.tokens.filled('_meta.batch.kwargs')

    def should_token_batch_finalise(self) -> bool:
        return self.has_token_batch_args() or self.has_token_batch_kwargs()

    @staticmethod
    def is_token_segment_item_extra_args(item: t.Any) -> bool:
        return Validate.is_string(item) and Validate.str_wrapped(item, '`')

    @staticmethod
    def is_token_segment_item_binding(item: t.Any) -> bool:
        return Validate.is_string(item) and (item == '?' or item.startswith(':'))
    
    @staticmethod
    def is_token_segment_item_binding_positional(item: t.Any) -> bool:
        return DataQuery.is_token_segment_item_binding(item) and item == '?'
    
    @staticmethod
    def is_token_segment_item_binding_named(item: t.Any) -> bool:
        return DataQuery.is_token_segment_item_binding(item) and item.startswith(':')