from __future__ import annotations
import re, hashlib, urllib.parse
from ansible_collections.aybarsm.utils.plugins.module_utils.aggregator import Aggregator

Helper = Aggregator.Tools.helper()
Data = Aggregator.Tools.data()
Validate = Aggregator.Tools.validate()

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
    def find(haystack, needle, reverse = False, before = True) -> str:
        index = haystack.rfind(needle) if reverse else haystack.find(needle)
        return str(haystack if index == -1 else (haystack[:index] if before else haystack[index + len(needle):]))
    
    @staticmethod
    def before(haystack, needle) -> str:
        return Str.find(haystack, needle)
    
    @staticmethod
    def before_last(haystack, needle) -> str:
        return Str.find(haystack, needle, reverse = True)
    
    @staticmethod
    def after(haystack, needle) -> str:
        return Str.find(haystack, needle, reverse = False, before = False)
    
    @staticmethod
    def after_last(haystack, needle) -> str:
        return Str.find(haystack, needle, reverse = True, before = False)
    
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

Aggregator.register_tool(Str)