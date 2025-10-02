class Tools:
    @staticmethod
    def helper():
        from ansible_collections.aybarsm.utils.plugins.module_utils.tools.helper import Helper
        return Helper
    
    @staticmethod
    def jinja():
        from ansible_collections.aybarsm.utils.plugins.module_utils.tools.jinja import Jinja
        return Jinja
    
    @staticmethod
    def str():
        from ansible_collections.aybarsm.utils.plugins.module_utils.tools.str import Str
        return Str
    
    @staticmethod
    def validate():
        from ansible_collections.aybarsm.utils.plugins.module_utils.tools.validate import Validate
        return Validate

    @staticmethod
    def data():
        from ansible_collections.aybarsm.utils.plugins.module_utils.tools.data import Data
        return Data
    
    @staticmethod
    def data_query():
        from ansible_collections.aybarsm.utils.plugins.module_utils.tools.data_query import DataQuery
        return DataQuery

    @staticmethod
    def validator():
        from ansible_collections.aybarsm.utils.plugins.module_utils.tools.validator import Validator
        return Validator

Helper = Tools.helper()
Jinja = Tools.jinja()
Str = Tools.str()
Validate = Tools.validate()
Data = Tools.data()
DataQuery = Tools.data_query()
Validator = Tools.validator()