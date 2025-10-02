from __future__ import annotations
import importlib, re, jinja2
from ansible_collections.aybarsm.utils.plugins.module_utils.aggregator import Aggregator

Helper = Aggregator.Tools.helper()

class Jinja:
    jinja2 = jinja2
    _instance = None
    _defaults = Aggregator.config()['defaults']['tools']['jinja']
    
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
        self._prefixes = '(' + ('|'.join(map(lambda op: re.escape(op), list(self._defaults['prefixes'].keys())))) + ')'

        for alias, info in self._defaults['module_map'].items():
            try:
                module = importlib.import_module(info["path"])
                modules[alias] = getattr(module, info["class"])
            except Exception as e:
                self._errors.append(f"Failed to import {alias} from {info['path']}: {e}")
                continue
        
        self.e = jinja2.Environment()
        
        for alias in modules.keys():
            is_test = self._defaults['module_map'][alias]['class'] == 'TestModule'
            segments = str(self._defaults['module_map'][alias]['path']).split('.')
            
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
        return re.compile(f'^{self._prefixes}').sub(lambda match: self._defaults['prefixes'][match.group(0)], op_name)
    
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

Aggregator.register_tool(Jinja)