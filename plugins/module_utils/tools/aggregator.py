def __collection():
    from ansible_collections.aybarsm.utils.plugins.module_utils.tools.collection import Collection
    return Collection

def __data_id_factory():
    import ansible_collections.aybarsm.utils.plugins.module_utils.tools.data_id_factory as DataIdFactory
    return DataIdFactory

def __fluent():
    from ansible_collections.aybarsm.utils.plugins.module_utils.tools.fluent import Fluent
    return Fluent

def __task():
    import ansible_collections.aybarsm.utils.plugins.module_utils.tools.task as ToolTask
    return ToolTask