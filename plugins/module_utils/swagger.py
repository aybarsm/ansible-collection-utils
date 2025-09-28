from ansible_collections.aybarsm.all.plugins import Aggregator as PrimaryAggregator
from ansible.module_utils.urls import open_url, fetch_url
from ansible.module_utils.basic import env_fallback

Validate = PrimaryAggregator.tools.validate
Data = PrimaryAggregator.tools.data
Str = PrimaryAggregator.tools.str
Helper = PrimaryAggregator.tools.helper
json = PrimaryAggregator.tools.json
yaml = PrimaryAggregator.tools.yaml
re = PrimaryAggregator.tools.re
itertools = PrimaryAggregator.tools.itertools
Any = PrimaryAggregator.tools.typing.Any
Mapping = PrimaryAggregator.tools.typing.Mapping
CONFIG = PrimaryAggregator.config

class Swagger:
    def __init__(self, cfg: dict = {}):
        base_config = CONFIG.copy()
        self._meta = {'cfg': Data.combine(Data.get(base_config, 'defaults.swagger', {}), cfg, recursive = True)}
        if 'defaults' in base_config:
            del base_config['defaults']
        self._set_meta('_', base_config.copy())
        self._set_meta('_.path.file.cache', self._get_path_file_cache())
        self._handle_cfg_changes()
        
        self._swagger = {}
        # self.docs_extract(swagger, self.cfg('extraction', {}))
    
    def get_validation_schema(self, path: str, method: str, remap: bool = True) -> dict:
        docs = self.swagger(f'paths.{path}.{method.lower()}')
        if Validate.blank(docs):
            raise ValueError(f'Path entry not found for {path} - {method.lower()} in docs')
        
        ret = self.prepare_validation_schema()
        ret = self._resolve_validation_schema_parameters(ret, docs)
        ret = self._resolve_validation_schema_security_definitions(ret, docs)
        if remap:
            ret = self._resolve_validation_schema_remapping(ret)

        return ret
    
    def _resolve_validation_schema_parameters(self, ret: dict, docs: dict) -> dict:
        if Validate.blank(docs.get('parameters', {})):
            return ret
        
        nest_key = self.get_validation_nest_key()

        for param in docs.get('parameters', {}):
            in_ = param.get('in', '')
            name_ = param.get('name', '')
            
            if nest_key not in ret[in_]:
                ret[in_][nest_key] = {}
            
            ret[in_][nest_key][name_] = self._build_component_validation_schema(param)
            
            if ret[in_][nest_key][name_]['required'] == True and ret[in_]['required'] == False:
                ret[in_]['required'] = True
            
            if 'default' in ret[in_]:
                del ret[in_]['default']
            
        return ret

    def _resolve_validation_schema_security_definitions(self, ret: dict, docs: dict) -> dict:
        sec_defs = self.swagger(f'securityDefinitions', {})
        secs = docs.get('security', self.swagger('security', []))
        secs = list(set([list(sec.keys())[0] for sec in secs if list(sec.keys())[0] in sec_defs]))
        # secs.append('basicAuth')
        
        if Validate.blank(secs):
            return ret
        
        nest_key = self.get_validation_nest_key()

        for sec_def_name in secs:
            sec_def = sec_defs[sec_def_name].copy()
            if Validate.blank(sec_def):
                raise ValueError(f'Security definition for [{sec_def_name}] could not be found')

            type_ = sec_def.get('type', '')
            if type_ not in ['apiKey', 'basic']:
                raise ValueError(f'Unknown security type [{type_}]')

            sec_def['required'] = sec_def.get('required', len(secs) == 1)

            if type_ == 'basic':
                sec_def['type'] = 'string'
                for name_ in ['url_username', 'url_password']:
                    ret[name_] = self._build_component_validation_schema(sec_def)
                if self.is_validation_ansible():
                    ret['url_password']['no_log'] = True
            else:
                in_ = sec_def.get('in', '')
                name_ = sec_def.get('name', '')
                
                if nest_key not in ret[in_]:
                    ret[in_][nest_key] = {}

                ret[in_][nest_key][name_] = self._build_component_validation_schema(sec_def)
                if self.is_validation_ansible():
                    ret[in_][nest_key][name_]['no_log'] = True

                if ret[in_][nest_key][name_]['required'] == True and ret[in_]['required'] == False:
                    ret[in_]['required'] = True
                
                if 'default' in ret[in_]:
                    del ret[in_]['default']
        
        return ret
    
    def _resolve_validation_schema_remapping(self, ret: dict[str, str]) -> dict:
        remap = self.remappings()
        overwrite = self.cfg('remap_overwrite', False)
        ignore_missing = self.cfg('remap_ignore_missing', False)
        if Validate.blank(remap['validation']):
            return ret
        
        cleanup = []
        for source, target in remap['validation'].items(): #type: ignore
            if not Data.has(ret, source):
                if ignore_missing:
                    continue
                else:
                    raise ValueError(f'Remapping source key [{source}] does not exist')
            
            if not overwrite and Data.has(ret, target):
                raise ValueError(f'Remapping target key [{target}] already exists')
            
            Data.set(ret, target, Data.get(ret, source))
            Data.forget(ret, source)

            source_segments = source.split('.')
            if Validate.is_int_odd(len(source_segments)):
                source_segments = source_segments[:-1]

            cleanup.extend(map('.'.join, itertools.accumulate(itertools.batched(source_segments, n=2), lambda x, y: x + y)))
        
        cleanup = Data.dot_sort_keys(list(set(cleanup)), asc = False)
        for dest in cleanup:
            dest_master = Str.before_last(dest, '.')
            if Data.has(ret, dest) and Validate.blank(Data.get(ret, dest, {})):
                if dest.count('.') > 1:
                    Data.forget(ret, dest_master)
                else:
                    Data.forget(ret, dest)
                    Data.set(ret, f'{dest_master}.required', False)
                    Data.set(ret, f'{dest_master}.default', {})

        return ret
    
    def get_normalised_nested_key(self, key: str, only_base: bool = False) -> str:
        if '.' not in key:
            return key
        
        nest_key = self.get_validation_nest_key()
        ret = re.sub('\\.+', '.', key).replace(f'.{nest_key}', '')
        
        return ret if only_base else ret.replace('.', f'.{nest_key}.')

    def get_ansible_module_kwargs(self, path: str, method: str) -> dict:
        validation = self.get_validation_schema(path, method)
        nest_key = 'schema' if self.is_validation_cerberus() else 'options'

        return validation
    
    def prepare_validation_schema(self) -> dict:
        if self.is_validation_ansible():
            ret = self.cfg('ansible.defaults.kwargs.argument_spec', {}).copy()
        else:
            ret = {}

        for segment in self.cfg('segments.keys', []):
            for default_key, default_val in self.cfg('segments.defaults', {}).items():
                key = f'{segment}.{default_key}'
                Data.set(ret, key, default_val)

        return ret
    
    def _build_component_validation_schema(self, item: dict) -> dict:
        ret = {
            'type': item.get('type', ''),
            'required': item.get('required', False),
        }

        props_ = Data.get(item, 'properties', Data.get(item, 'schema.properties', {}))
        items_ = Data.get(item, 'items', {})
        if Validate.filled(item.get('default', '')):
            ret['default'] = item.get('default', '')

        if Validate.blank(ret['type']):
            if Validate.filled(props_):
                ret['type'] = 'object'
            elif Validate.filled(items_):
                ret['type'] = 'array'
        
        if Validate.blank(ret['type']):
            self._error_value('Type could not be resolved', ret)
        
        ret['type'] = self.get_validation_type(ret['type'], item.get('format', ''))

        if (ret['type'] == 'list' and Validate.blank(items_)) or (ret['type'] == 'dict' and Validate.blank(props_)):
            self._error_value(f'Schema does not have children', ret)
        
        if Validate.filled(item.get('enum', {})):
            enum_key = 'allowed' if self.is_validation_cerberus() else 'choices'
            ret[enum_key] = item.get('enum', {}).copy()
        
        if ret['type'] not in ['list', 'dict']:
            return ret

        nest_key = 'schema' if self.is_validation_cerberus() else 'options'
        if ret['type'] == 'list':
            if not self.is_validation_cerberus():
                options = self._build_component_validation_schema(items_)
                ret['elements'] = options['type']
                if options['type'] == 'dict':
                    ret['options'] = options['options']
            else:
                ret[nest_key] = self._build_component_validation_schema(items_)
            
            return ret

        ret[nest_key] = {}
        for child_key, child_val in props_.items():
            child_ref = child_val.copy()
            if Validate.is_sequence(ret['required']) and child_key in ret['required']:
                child_ref['required'] = True
            ret[nest_key][child_key] = self._build_component_validation_schema(child_ref)
        
        if Validate.is_sequence(ret['required']):
            ret['required'] = False
            
        return ret

    def _get_value(self, container, key = '', default = None) -> Any:   
        return Data.get(container, key, default) if Validate.filled(key) else container

    def meta(self, key: str  = '', default: Any = None) -> Any:
        return self._get_value(self._meta, key, default)
    
    def cfg(self, key: str  = '', default: Any = None) -> Any:
        return self._get_value(self._meta.get('cfg', {}), key, default)
    
    def params(self, key: str  = '', default: Any = None) -> Any:
        new_key = None
        if Validate.filled(key):
            param_key = Str.start(key, 'params.')
            if not Data.has(self._meta, param_key):
                remap = self.remappings()
                target = self.get_normalised_nested_key(key, True)
                for dest in [key, target]:
                    for src in ['params', 'params_flipped']:
                        if dest in remap[src]:
                            new_key = remap[src][dest]
                            break
                    
                    if new_key:
                        break
        
        if new_key:
            key = new_key

        return self._get_value(self._meta.get('params', {}), key, default)

    def remappings(self) -> dict:
        remap = self.cfg('remap', {})
        ret = {'validation': {}, 'params': {}}
        
        if Validate.blank(remap):
            return ret
        
        for map_src, map_trg in remap.items(): #type: ignore
            validation_source = self.get_normalised_nested_key(map_src)
            validation_target = self.get_normalised_nested_key(map_trg)
            ret['validation'][validation_source] = validation_target
            param_source = self.get_normalised_nested_key(map_src, True)
            param_target = self.get_normalised_nested_key(map_trg, True)
            ret['params'][param_source] = param_target
        
        ret['validation'] = dict(Data.dot_sort_keys(ret['validation'], asc = False))
        ret['validation_flipped'] = Data.flip(ret['validation'].copy())
        ret['params'] = dict(Data.dot_sort_keys(ret['params'], asc = False))
        ret['params_flipped'] = Data.flip(ret['params'].copy())

        return ret

    def set_cfg(self, key: str, value: Any) -> None:
        Data.set(self._meta['cfg'], key, value)
        self._handle_cfg_changes()
    
    def _handle_cfg_changes(self) -> None:
        from ansible.module_utils.basic import _load_params
        ansible_load_params = self.cfg('ansible.load_params', False)
        if  ansible_load_params == True and not self.has_meta('_.params'):
            self._set_meta('_.params', dict(_load_params()))
        
        path_file_cache = self.meta('_.path.file.cache')
        if Validate.filled(path_file_cache) and not self.has_meta('_.cache'):
            if Validate.file_exists(path_file_cache):
                self._set_meta('_.cache', json.loads((lambda f: f.read())(open(path_file_cache))))
            else:
                self._set_meta('_.cache', {'meta': {}, 'docs': {}})
    
    def _save_cache(self):
        path_file_cache = self.meta('_.path.file.cache')
        if Validate.filled(path_file_cache):
            with open(path_file_cache, "w", encoding="utf-8") as f:
                json.dump(self.meta('_.cache'), f, ensure_ascii=False)

    def swagger(self, key: str = '', default: Any = None) -> Any:
        return self._get_value(self._swagger, key, default)
    
    def _set_meta(self, key: str, value: Any) -> None:
        Data.set(self._meta, key, value)
    
    def _forget_meta(self, key: str) -> None:        
        Data.forget(self._meta, key)
    
    def has_meta(self, key: str) -> bool:
        return Data.has(self._meta, key)
    
    def is_validation_ansible(self):
        return self.cfg('ansible.validation', False) == True
    
    def is_validation_cerberus(self):
        return not self.is_validation_ansible()
    
    def get_validation_type(self, type_: str, format_: str | None) -> str:
        if self.is_validation_cerberus():
            return self.get_cerberus_type(type_, format_)
        else:
            return self.get_ansible_type(type_)
    
    def get_validation_nest_key(self) -> str:
        return 'schema' if self.is_validation_cerberus() else 'options'
    
    def _get_path_file_cache(self) -> str:
        filename = 'cache_tool_swagger.json'
        path_tmp = self.meta('_.path.dir.tmp')
        if not Validate.is_dir_writable(path_tmp):
            return Helper.path_tmp(filename)
        else:
            return Helper.join_paths(path_tmp, filename)

    @staticmethod
    def get_cerberus_type(type_: str, format_: str | None) -> str:
        mapping = {
            ('string', None): 'string',
            ('string', 'byte'): 'binary',
            ('string', 'binary'): 'binary',
            ('string', 'password'): 'string',
            ('string', 'date'): 'date',
            ('string', 'date-time'): 'datetime',
            ('number', None): 'float',
            ('number', 'float'): 'float',
            ('number', 'double'): 'float',
            ('integer', None): 'integer',
            ('integer', 'int32'): 'integer',
            ('integer', 'int64'): 'integer',
            ('boolean', None): 'boolean',
            ('array', None): 'list',
            ('object', None): 'dict',
        }

        cerberus_type = mapping.get((type_, format_)) or mapping.get((type_, None))

        return cerberus_type if cerberus_type else 'string'
    
    @staticmethod
    def get_ansible_type(type_: str) -> str:
        match type_:
            case 'int' | 'integer':
                return 'integer'
            case 'bool' | 'boolean':
                return 'bool'
            case 'float' | 'double' | 'number':
                return 'float'
            case 'list' | 'array' | 'arr':
                return 'list'
            case 'dict' | 'object':
                return 'dict'
            case 'path' | 'file':
                return 'path'
            case _:
                return 'str'

    @staticmethod
    def _error_value(msg: str, item: dict) -> None:
        parts = [f'[{msg.strip()}]']

        info = []
        infoable = Data.only_with(item, 'name', 'parent_key', 'in', 'type', 'path', 'method')
        
        if Validate.filled(infoable):
            for key, value in infoable.items(): #type: ignore
                if Validate.blank(value):
                    continue
                title = str(key).title()
                info.append(f'{title}: {str(value)}')
    
        parts.append(' - '.join(info))
        raise ValueError(' '.join(parts))
    
    @staticmethod
    def resolve_ref_key(ref) -> str:
        return Str.replace(Str.chop_start(ref, '#/'), '/', '.')
    
    @staticmethod
    def docs_extract(swagger: dict, cfg: dict = {}):
        pattern_ = Data.get(cfg, 'ref_pattern', '.*\\.\\$ref.*$')
        pattern = re.compile(pattern_)
        ret = swagger.copy()
        dotted = Data.dot(swagger)
        dotted_keys = [item for item in dotted.keys() if pattern.match(item)]
        ref_keys = Data.dot_sort_keys(dotted_keys, asc = False)
        ref_map = Data.dot_sort_keys(Data.only_with(dotted, *ref_keys, no_dot = True), asc = False) #type: ignore
        # ref_map = dict(reversed(sorted(dict(Data.only_with(dotted, *ref_keys, no_dot = True)).items(), key=lambda item: item[0].count('.')))) #type: ignore
        ref_sources_keys = [Swagger.resolve_ref_key(ref_source_key) for ref_source_key in set(ref_map.values())] #type: ignore
        ref_sources_dotted = Data.dot(Data.only_with(swagger, *ref_sources_keys))
        ref_sources_dotted_keys = [item for item in ref_sources_dotted.keys() if pattern.match(item)]
        ref_sources_ref_keys_primary = Data.dot_sort_keys(ref_sources_dotted_keys, asc = False)
        ref_sources_ref_keys_secondary = [item for item in ref_keys if item not in ref_sources_ref_keys_primary]
        iterate_ref_keys = ref_sources_ref_keys_primary + ref_sources_ref_keys_secondary #type: ignore
    
        for ref_key in iterate_ref_keys:
            ref_source = Data.get(ret, ref_key)
            if Validate.blank(ref_source):
                continue
            
            ref_source = Swagger.resolve_ref_key(ref_source)
            ref = Data.get(swagger, ref_source, {})
            
            if Validate.blank(ref):
                raise ValueError(f'Could not extract reference source {ref_key} [{ref_source}]')
            
            ref_dest = re.sub(r"\.\$ref(?!.*\.\$ref)", '', ref_key)
            Data.forget(ret, ref_key)
            Data.set(ret, ref_dest, ref.copy())
        
        return ret
    
    def load_swagger(self, source: Mapping | str) -> None:
        if Validate.is_mapping(source):
            swagger = dict(source) #type: ignore
        elif Validate.str_is_url(str(source)):
            swagger = json.loads(open_url(url = str(source), validate_certs = self.params('docs_validate_certs', True)).read().decode('utf-8'))
        elif Validate.file_exists(source):
            swagger = json.loads((lambda f: f.read())(open(str(source))))
        elif Validate.str_is_json(str(source)):
            swagger = json.loads(str(source))
        elif Validate.str_is_yaml(str(source)):
            swagger = yaml.safe_load(str(source))
        else:
            raise ValueError('Unable to identify swagger source type to load')
        
        self._swagger = self.docs_extract(swagger, self.cfg('extraction', {}))