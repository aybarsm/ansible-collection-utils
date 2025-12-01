import typing as t
import time
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    _ansible, _convert, _data, _utils, _validate
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.data_query import DataQuery

Ansible = _ansible()
Convert = _convert()
Data = _data()
Utils = _utils()
Validate = _validate()

class DataQueryExecutor(DataQuery):
    def execute(self) -> t.Any:
        if self.is_mode_debug():
            start = time.perf_counter()

        ret_default = self.get_default_return()
        if Validate.blank(self.data):
            return ret_default

        if not self.context:
            raise RuntimeError('Context is not set to execute tests')
        
        token_group = self.get_executor_initial_token_group()
        ret = []
        for item in self.get_executor_data():
            res = self._execute_token_group([item], token_group)
            if Validate.filled(res):
                ret.append(res[0])
            
            if self.is_first_result() and Validate.filled(ret):
                break

        if Validate.filled(ret):
            ret = [item for idx, item in enumerate(self.data) if idx in set(Data.pluck(ret, 'key'))]

            if self.is_first_result():
                ret = ret[0]
        else:
            ret = ret_default
        
        if self.is_mode_debug():
            end = time.perf_counter()
            ret = {'data': ret, '_meta': {'duration': f'{end - start:.6f} seconds'}}

        return ret

    def _execute_token_group(self, data: list[dict[str, t.Any]], token_group: dict[str, t.Any]) -> list[dict[str, t.Any]]:
        if Validate.blank(data):
            return []

        queue = self._resolve_token_group_execution_queue(token_group)
        
        if token_group['cond'] == 'all':
            return self._execute_condition_all(data, queue)
        elif token_group['cond'] == 'any':
            return self._execute_condition_any(data, queue)
        
        return data

    def _execute_condition_all(self, data: list[dict[str, t.Any]], queue: list[dict[str, t.Any]]) -> list[dict[str, t.Any]]:
        current_data = data

        for item in queue:
            if Validate.blank(current_data):
                return []

            if item['type'] == 'test':
                current_data = self._execute_test(current_data, item['payload'])
            elif item['type'] == 'sub':
                current_data = self._execute_token_group(current_data, item['payload'])

        return current_data

    def _execute_condition_any(self, data: list[dict[str, t.Any]], queue: list[dict[str, t.Any]]) -> list[dict[str, t.Any]]:
        results = []
        candidates = Convert.as_copied(data)
        
        for item in queue:
            if Validate.blank(candidates):
                break

            matches = []
            if item['type'] == 'test':
                matches = self._execute_test(candidates, item['payload'])
            elif item['type'] == 'sub':
                payload = item['payload'] if isinstance(item, dict) else item
                matches = self._execute_token_group(candidates, payload)
            
            if Validate.filled(matches):
                results = list(Data.append(results, '', Data.pluck(matches, 'key'), extend=True, unique=True, sort=True))
                candidates = [item for item in candidates if item['key'] not in results]
        
        if Validate.blank(results):
            return []
        else:
            return [item for item in data if item['key'] in set(results)]

    def _execute_test(self, data: list[dict[str, t.Any]], test: dict[str, t.Any]) -> list[dict[str, t.Any]]:
        args = list(test['args'])
        kwargs = dict(test['kwargs'])
        
        if self.is_mod_attr():
            data = self._resolve_test_eligible_data(data, args[0])

        args.insert(0, data)
        args.insert(0, self.context)

        if test['negate']:
            return list(Ansible.filter_rejectattr(*args, **kwargs))
        else:
            return list(Ansible.filter_selectattr(*args, **kwargs))
    
    def get_executor_initial_token_group(self) -> dict:
        tokens = self.get_tokens()
        ret = tokens['0']

        for key_ in sorted(tokens.keys()):
            if key_ == '0':
                continue

            if 'subs' not in ret:
                ret['subs'] = {}
            
            ret['subs'][key_] = tokens[key_]

        return ret
    
    def get_executor_data(self) -> list:
        return Convert.to_items(Convert.as_copied(self.data))
    
    @staticmethod
    def _resolve_test_eligible_data(data: list[dict[str, t.Any]], data_key: str) -> list[dict[str, t.Any]]:
        return [item for item in data if Data.has(item, data_key)]
    
    @staticmethod
    def _resolve_token_group_execution_queue(token_group: dict[str, t.Any]) -> list[dict[str, t.Any]]:
        ret = []

        if Validate.filled(token_group.get('tests', [])):
            for test in token_group['tests']:
                ret.append({'type': 'test', 'payload': test})
                
        if Validate.filled(token_group.get('subs', [])):
            for sub in dict(sorted(dict(token_group['subs']).items())).values():
                ret.append({'type': 'sub', 'payload': sub})
        
        return ret