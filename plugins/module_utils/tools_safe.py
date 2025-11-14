from typing import Sequence, Mapping, Iterable, Any

class Helper:
    @staticmethod
    def to_iterable(data: Any) -> list[Any]:
        return list(data) if Validate.is_sequence(data) else [data]
    
    @staticmethod
    def to_type_name(data)-> str:
        return type(data).__name__

class Validate:
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
    def is_sequence(data, include_strings = False):
        if not include_strings and Validate.is_string(data):
            return False
        
        return isinstance(data, Sequence)
    
    @staticmethod
    def is_mapping(data):        
        return isinstance(data, Mapping)
    
    @staticmethod
    def is_undefined(data):
        return Validate.is_object(data) and type(data).__name__.startswith('AnsibleUndefined')
    
    @staticmethod
    def is_omitted(data):
        return Validate.is_string(data) and str(data).startswith('__omit_place_holder__')

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
    def is_int_even(data: int) -> bool:
        return data % 2 == 0
    
    @staticmethod
    def is_int_odd(data: int) -> bool:
        return not Validate.is_int_even(data)
    
    @staticmethod
    def is_iterable_of_iterables(data):
        return Validate.is_iterable(data) and all(Validate.is_iterable(item) for item in data)

    @staticmethod
    def is_iterable_of_mappings(data):
        return Validate.is_iterable(data) and all(Validate.is_mapping(item) for item in data)
    
    @staticmethod
    def is_iterable_of_strings(data):
        return Validate.is_iterable(data) and all(Validate.is_string(item) for item in data)
    
    @staticmethod
    def is_iterable_of_booleans(data):
        return Validate.is_iterable(data) and all(Validate.is_bool(item) for item in data)
    
    @staticmethod
    def is_mapping_of_iterables(data):
        return Validate.is_mapping(data) and all(Validate.is_iterable(item) for item in data.values())
    
    @staticmethod
    def is_mapping_of_mappings(data):
        return Validate.is_mapping(data) and all(Validate.is_mapping(item) for item in data.values())
    
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
            case 'iterable':
                return Validate.is_iterable(data)
            case 'sequence':
                return Validate.is_sequence(data)
            case 'mapping':
                return Validate.is_mapping(data)
            case 'callable':
                return Validate.is_callable(data)
            case 'iterableofiterables':
                return Validate.is_iterable_of_iterables(data)
            case 'iterableofmappings':
                return Validate.is_iterable_of_mappings(data)
            case 'iterableofstrings':
                return Validate.is_iterable_of_strings(data)
            case 'iterableofbooleans':
                return Validate.is_iterable_of_booleans(data)
            case 'mappingofiterables':
                return Validate.is_mapping_of_iterables(data)
            case 'mappingofmappings':
                return Validate.is_mapping_of_mappings(data)
            case _:
                raise ValueError(f"require, {req} is not a valid type to check.")