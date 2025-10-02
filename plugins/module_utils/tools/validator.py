from __future__ import annotations
import cerberus
from ansible_collections.aybarsm.utils.plugins.module_utils.aggregator import Aggregator

Validate = Aggregator.Tools.validate()

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
    
    def _exec_required_conditional(self, constraint, field, value, when: bool = True):
        if not Validate.is_mapping(constraint):
            raise cerberus.SchemaError("The constraint for 'required_when' must be a mapping.")

        constraint = dict(constraint)
        keyword = 'when' if when else 'unless'

        for foreign_key, foreign_value in constraint.items():
            res = self.document.get(foreign_key) != foreign_value #type: ignore
            res = not res if not when else res
            if res:
                self._error(field, f"is required {keyword} {constraint}") #type: ignore
                break
    
    def _validate_required_when(self, constraint, field, value):
        """{'type': 'boolean'}"""
        self._exec_required_conditional(constraint, field, value)
    
    def _validate_required_unless(self, constraint, field, value):
        """{'type': 'boolean'}"""
        self._exec_required_conditional(constraint, field, value, False)

    def error_message(self) -> str:
        parts = []
        for key_name, error in (Data.dot(self.errors)).items(): #type: ignore
            parts.append(f'{key_name}: {error}')
        
        return ' | '.join(parts)

Aggregator.register_tool(Validator)