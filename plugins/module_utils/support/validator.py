import typing as t
from ansible_collections.aybarsm.utils.plugins.module_utils.aggregator import CONF_, Kit

class Validator(Kit.Cerberus().Validator):
    def __init__(self, *args, **kwargs):
        if Kit.Validate().blank(args):
            args = [
                kwargs.pop('schema', {}),
                kwargs.pop('ignore_none_values', False),
                kwargs.pop('allow_unknown', False),
                kwargs.pop('require_all', False),
                kwargs.pop('purge_unknown', False),
                kwargs.pop('purge_readonly', False),
            ]

        self.mandatory_validations = kwargs.pop('mandatory_validations', self.mandatory_validations)
        self.priority_validations = kwargs.pop('priority_validations', self.priority_validations)
        
        super().__init__(*args, **kwargs)
    
    def validate(self, document, schema=None, update=False, normalize=True):
        return super().validate(document, schema, update, normalize) #type: ignore
    
    def normalized(self, document, schema=None, always_return_document=False):
        return super().normalized(document, schema, always_return_document) #type: ignore

    def _lookup_path(self, path: str, prefix: str = '^')-> set:
        path = path.strip()
        prefix = prefix.strip()
        if Kit.Validate().filled(prefix):
            path = Kit.Str().start(path, prefix)
        
        return self._lookup_field(path) #type: ignore
    
    def _lookup_value(self, path: str, prefix: str = '^')-> t.Any:        
        return self._lookup_path(path, prefix)[-1] #type: ignore
    
    def _lookup_key(self, path: str, prefix: str = '^')-> t.Any:        
        return self._lookup_path(path, prefix)[0] #type: ignore
        
    def _check_blank_filled_conditional(
        self,
        value: t.Any,
        foreign_field: str, 
        foreign_value: t.Any, 
        mod: str, 
        expect_filled: bool,
        field: str = '',
    )-> t.Optional[str]:
        mod = mod.lower()

        if mod not in ['unless', 'when']:
            raise ValueError(f'[Rule: Conditional Blank/Filled] - Unknown mod [{mod}]. Available: when, unless')

        doc_value = self._lookup_value(foreign_field)
        expect_blank = not expect_filled
        expected_value = doc_value == foreign_value
        not_expected_value = not expected_value

        error_message = [
            'Must be',
            ('filled' if expect_filled else 'blank'),
            mod,
            f'[{foreign_field}]',
            'field set to',
            f'[{Kit.Convert().to_text(foreign_value)}]'
        ]
        error_message = ' '.join(error_message)
        
        if (mod == 'when' and expected_value) or (mod == 'unless' and not_expected_value):
            if (expect_filled and not Kit.Validate().filled(value)) or (expect_blank and not Kit.Validate().blank(value)):
                return error_message
        
        return None

    def _exec_filled_blank_conditional(self, constraint: t.Mapping, field: str, value: t.Any, mod: str, filled: bool, **kwargs)-> None:
        if constraint == None:
            return
        for field_, value_ in constraint.items():
            error_message = self._check_blank_filled_conditional(value, field_, value_, mod, filled, field)
            if error_message != None:
                self._error(field, error_message) #type: ignore
                break
    
    def _validate_filled_when(self, constraint: t.Mapping, field: str, value: t.Any):
        """{'type': 'dict', 'empty': False, 'default': {}}"""
        self._exec_filled_blank_conditional(constraint, field, value, 'when', True)
    
    def _validate_filled_unless(self, constraint: t.Mapping, field: str, value: t.Any):
        """{'type': 'dict', 'empty': False, 'default': {}}"""
        self._exec_filled_blank_conditional(constraint, field, value, 'unless', True)
    
    def _validate_blank_when(self, constraint: t.Mapping, field: str, value: t.Any):
        """{'type': 'dict', 'empty': False, 'default': {}}"""
        self._exec_filled_blank_conditional(constraint, field, value, 'when', False)

    def _validate_blank_unless(self, constraint: t.Mapping, field: str, value: t.Any):
        """{'type': 'dict', 'empty': False, 'default': {}}"""
        self._exec_filled_blank_conditional(constraint, field, value, 'unless', False)
    
    def _validate_path_exists(self, constraint, field, value):
        """{'type': 'boolean'}"""
        if constraint is True and not Kit.Validate().fs_path_exists(value):
            self._error(field, f"Must be an [{value}] existing path") #type: ignore
        elif constraint is False and Kit.Validate().fs_path_exists(value):
            self._error(field, f"Must be a [{value}] missing path") #type: ignore
    
    def _validate_file_exists(self, constraint, field, value):
        """{'type': 'boolean'}"""
        if constraint is True and not Kit.Validate().fs_file_exists(value):
            self._error(field, f"Must be an [{value}] existing file") #type: ignore
        elif constraint is False and Kit.Validate().fs_file_exists(value):
            self._error(field, f"Must be a [{value}] missing file") #type: ignore
    
    def _validate_dir_exists(self, constraint, field, value):
        """{'type': 'boolean'}"""
        if constraint is True and not Kit.Validate().fs_dir_exists(value):
            self._error(field, f"Must be an [{value}] existing directory") #type: ignore
        elif constraint is False and Kit.Validate().fs_dir_exists(value):
            self._error(field, f"Must be a [{value}] missing directory") #type: ignore
    
    def _exec_validate_regex(self, value, key_: str)-> bool:
        if not isinstance(value, str):
            return False
        
        return bool(CONF_['regex'][key_].match(value))
        
    def _exec_validate_type_ip(self, value, version: t.Literal[4, 6, 46], type_: t.Literal['address', 'subnet', ''] = '')-> bool:
        if not isinstance(value, str):
            return False
        
        suffix = f'_{type_}' if Kit.Validate().filled(type_) else ''
        keys = [f'ipv4{suffix}', f'ipv6{suffix}'] if version == 46 else [f'ipv{str(version)}{suffix}']
        
        for key_ in keys:
            if self._exec_validate_regex(value, key_):
                return True
            
        return False
    
    def _validate_type_ipv4(self, value):
        """ Enables 'type': 'ipv4' in schema """
        return self._exec_validate_type_ip(value, 4)
    
    def _validate_type_ipv4_address(self, value):
        """ Enables 'type': 'ipv4_address' in schema """
        return self._exec_validate_type_ip(value, 4, 'address')

    def _validate_type_ipv4_subnet(self, value):
        """ Enables 'type': 'ipv4_subnet' in schema """
        return self._exec_validate_type_ip(value, 4, 'subnet')
    
    def _validate_type_ipv6(self, value):
        """ Enables 'type': 'ipv6' in schema """
        return self._exec_validate_type_ip(value, 6)
    
    def _validate_type_ipv6_address(self, value):
        """ Enables 'type': 'ipv6_address' in schema """
        return self._exec_validate_type_ip(value, 6, 'address')

    def _validate_type_ipv6_subnet(self, value):
        """ Enables 'type': 'ipv6_subnet' in schema """
        return self._exec_validate_type_ip(value, 6, 'subnet')
    
    def _validate_type_ip(self, value):
        """ Enables 'type': 'ip' in schema """
        return self._exec_validate_type_ip(value, 46)
    
    def _validate_type_ip_address(self, value):
        """ Enables 'type': 'ip_address' in schema """
        return self._exec_validate_type_ip(value, 46, 'address')
    
    def _validate_type_ip_subnet(self, value):
        """ Enables 'type': 'ip_address' in schema """
        return self._exec_validate_type_ip(value, 46, 'subnet')
    
    def _validate_type_mac_address(self, value):
        """ Enables 'type': 'mac_address' in schema """
        return self._exec_validate_regex(value, 'mac_address')

    def error_message(self) -> str:
        parts = []
        for key_name, error in (Kit.Data().dot(self.errors)).items(): #type: ignore
            parts.append(f'{key_name}: {error}')
        
        return ' | '.join(parts)