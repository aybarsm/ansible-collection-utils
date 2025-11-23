import typing as T
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    __ansible, __convert, __data, __validate
)
from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.data_query import DataQuery

Ansible = __ansible()
Convert = __convert()
Data = __data()
Validate = __validate()

class DataQueryExecutor:
    def __init__(self, data_query: DataQuery):
        self.dq: DataQuery = data_query

    def execute(self) -> list[dict[str, T.Any]]:
        return self._process_group(self.dq.get_executor_data(), self.dq._get_executor_tokens())

    def _process_group(self, data: list[dict[str, T.Any]], token_group: dict[str, T.Any]) -> list[dict[str, T.Any]]:
        if Validate.blank(data):
            return []

        condition = token_group['cond']
        queue = self._resolve_token_group_queue(token_group)

        if condition == 'all':
            return self._process_all(data, queue)
        elif condition == 'any':
            return self._process_any(data, queue)
        
        return data

    def _process_all(self, data: list[dict[str, T.Any]], queue: list[dict[str, T.Any]]) -> list[dict[str, T.Any]]:
        current_data = data

        for item in queue:
            if Validate.blank(current_data):
                return []

            if item['type'] == 'test':
                current_data = self._execute_test(current_data, item['payload'])
            elif item['type'] == 'sub':
                current_data = self._process_group(current_data, item['payload'])

        return current_data

    def _process_any(self, data: list[dict[str, T.Any]], queue: list[dict[str, T.Any]]) -> list[dict[str, T.Any]]:
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
                matches = self._process_group(candidates, payload)
            
            if Validate.filled(matches):
                results = Data.append(results, '', Data.pluck(matches, 'key'), extend=True, unique=True)
                candidates = [item for item in candidates if item['key'] not in results]
        
        if Validate.blank(results):
            return []
        else:
            return [item for item in data if item['key'] in set(results)]

    def _execute_test(self, data: list[dict[str, T.Any]], test: dict[str, T.Any]) -> list[dict[str, T.Any]]:
        args = list(test['args'])
        kwargs = dict(test['kwargs'])
        
        if self.dq.is_mod_attr():
            data = self._resolve_eligible_data(data, args[0])

        args.insert(0, data)
        args.insert(0, self.dq.context)

        if test['negate']:
            return Ansible.filter_rejectattr(*args, **kwargs)
        else:
            return Ansible.filter_selectattr(*args, **kwargs)
    
    @staticmethod
    def _resolve_eligible_data(data: list[dict[str, T.Any]], data_key: str) -> list[dict[str, T.Any]]:
        return [item for item in data if Data.has(item, data_key)]
    
    @staticmethod
    def _resolve_token_group_queue(token_group: dict[str, T.Any]) -> list[dict[str, T.Any]]:
        ret = []

        if Validate.filled(token_group.get('tests', [])):
            for test in token_group['tests']:
                ret.append({'type': 'test', 'payload': test})
                
        if Validate.filled(token_group.get('subs', [])):
            for sub in dict(sorted(dict(token_group['subs']).items())).values():
                ret.append({'type': 'sub', 'payload': sub})
        
        return ret