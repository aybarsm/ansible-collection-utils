class ToolAgggregator:
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

class UtilAgggregator:
    @staticmethod
    def swagger():
        from ansible_collections.aybarsm.utils.plugins.module_utils.swagger import Swagger
        return Swagger
    
    @staticmethod
    def powerdns_api():
        from ansible_collections.aybarsm.utils.plugins.module_utils.powerdns_api import PowerdnsApi
        return PowerdnsApi

class AbstractAgggregator:
    @staticmethod
    def plugin_action():
        from ansible_collections.aybarsm.utils.plugins.module_utils.abstracts.plugin_action import PluginAction
        return PluginAction

class Registry:
    @staticmethod
    def config():
        import pathlib
        path_root = pathlib.Path(__file__).parent.parent

        return {
            'path': {
                'dir': {
                    'root': str(path_root),
                    'tmp' : str(path_root.joinpath('.tmp')),
                }
            }
        }
    
    class Tools:
        Helper = ToolAgggregator.helper()
        Jinja = ToolAgggregator.jinja()
        Str = ToolAgggregator.str()
        Validate = ToolAgggregator.validate()
        Data = ToolAgggregator.data()
        DataQuery = ToolAgggregator.data_query()
        Validator = ToolAgggregator.validator()
    
    class Utils:
        Swagger = UtilAgggregator.swagger()
        PowerdnsApi = UtilAgggregator.powerdns_api()
    
    class Abstracts:
        PluginAction = AbstractAgggregator.plugin_action()