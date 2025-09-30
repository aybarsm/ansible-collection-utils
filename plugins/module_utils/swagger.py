from ansible_collections.aybarsm.utils.plugins import Aggregator as PrimaryAggregator
from ansible.module_utils.urls import open_url, fetch_url

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
        defaults = Data.get(base_config, 'defaults.swagger', {})
        Data.forget(base_config, 'defaults')
        essentials = Data.get(defaults, '_', {})
        Data.forget(defaults, '_')
        cfg = Data.combine(defaults, cfg, essentials, base_config, {'_': essentials}, recursive = True)
        Data.set(cfg, 'path.file.cache', self._get_path_file_cache(Data.get(cfg, 'path.dir.tmp')))
        
        self._meta = {'cfg': cfg}
        self._swagger = {}
        # self.docs_extract(swagger, self.cfg('extraction', {}))
    
    def get_validation_schema(self, path: str, method: str, remap: bool = True) -> dict:
        docs = self.swagger(f'paths.{path}.{method.lower()}')
        if Validate.blank(docs):
            raise ValueError(f'Path entry not found for {path} - {method.lower()} in docs')
        
        ret = self._prepare_validation_schema()
        ret = self._resolve_validation_schema_parameters(ret, docs)
        ret = self._resolve_validation_schema_security_definitions(ret, docs)
        ret = self._resolve_validation_schema_real_key_paths(ret)

        if remap:
            ret = self._resolve_validation_schema_remapping(ret)
        
        # ret = self._resolve_validation_schema_ignores(ret)
        ret = self._finalise_validation_schema(ret)
        
        # Data.forget(ret, '_')
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
        secs.append('basicAuth')
        
        if Validate.blank(secs):
            return ret
        
        nest_key = self.get_validation_nest_key()

        meta = {
            'mutually_exclusive': [],
            'required_one_of': [],
            'required_together': [],
        }
        
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

                meta['required_together'].append(['url_username', 'url_password'])
                if len(secs) > 1:
                    meta['mutually_exclusive'].append('url_username')
                    meta['required_one_of'].append('url_username')
            else:
                in_ = sec_def.get('in', '')
                name_ = sec_def.get('name', '')
                
                if nest_key not in ret[in_]:
                    ret[in_][nest_key] = {}

                ret[in_][nest_key][name_] = self._build_component_validation_schema(sec_def)
                if self.is_validation_ansible():
                    ret[in_][nest_key][name_]['no_log'] = True

                if len(secs) > 1:
                    meta['mutually_exclusive'].append(f'{in_}.{name_}')
                    meta['required_one_of'].append(f'{in_}.{name_}')

                if ret[in_][nest_key][name_]['required'] == True and ret[in_]['required'] == False:
                    ret[in_]['required'] = True
                
                if 'default' in ret[in_]:
                    del ret[in_]['default']

        for meta_key, meta_val in meta.items():
            if Validate.blank(meta_val):
                continue

            current_val = Data.get(ret, f'_.{meta_key}', [])
            current_val.append(meta_val.copy())
            Data.set(ret, f'_.{meta_key}', current_val)

        return ret
    
    def _resolve_validation_schema_real_key_paths(self, ret: dict) -> dict:
        remap = self.cfg('remap', {})
        ret_dot = dict(Data.dot_sort_keys(Data.dot(ret), asc=False))
        
        for map_src, map_trg in remap.items(): #type: ignore
            source = re.sub('\\.+', '.', map_src)
            

        ignore = self.cfg('ignore', {})

        # ret = {'raw': remap.copy(), 'validation': {}, 'validation_flipped': {}, 'params': {}, 'params_flipped': {}}
        
        # if Validate.blank(remap):
        #     return ret
        
        # for map_src, map_trg in remap.items(): #type: ignore
        #     validation_source = self.get_normalised_nested_key(map_src)
        #     validation_target = self.get_normalised_nested_key(map_trg)
        #     ret['validation'][validation_source] = validation_target
        #     param_source = self.get_normalised_nested_key(map_src, True)
        #     param_target = self.get_normalised_nested_key(map_trg, True)
        #     ret['params'][param_source] = param_target
        
        # ret['validation'] = dict(Data.dot_sort_keys(ret['validation'], asc = False))
        # ret['validation_flipped'] = Data.flip(ret['validation'].copy())
        # ret['params'] = dict(Data.dot_sort_keys(ret['params'], asc = False))
        # ret['params_flipped'] = Data.flip(ret['params'].copy())

        return ret
    
    def _resolve_validation_schema_remapping(self, ret: dict) -> dict:
        remap = self.cfg('remap', {})
        meta = {}
        


        overwrite = self.cfg('remap_overwrite', False)
        ignore_missing = self.cfg('remap_ignore_missing', False)
        if Validate.blank(remap['validation']):
            return ret
        
        for source, target in remap['validation'].items(): #type: ignore
            if not Data.has(ret, source):
                if ignore_missing:
                    continue
                else:
                    raise ValueError(f'Remapping source key [{source}] does not exist')
            
            if not overwrite and Data.has(ret, target):
                raise ValueError(f'Remapping target key [{target}] already exists')
            
            component = Data.get(ret, source).copy()
            component = Data.combine(component, self.cfg(f'defaults.{target}._validation', {}))
            Data.set(ret, target, component)
            Data.forget(ret, source)

        return ret
    
    # def _resolve_validation_schema_ignores(self, ret: dict) -> dict:
    #     for ignore in self.ignored():
    #         Data.forget(ret, ignore)
        
    #     return ret
    
    def _finalise_validation_schema(self, ret: dict) -> dict:
        nest_key = self.get_validation_nest_key()
        
        # Cleanup:
        for key, value in (dict(Data.dot_sort_keys(Data.dot(ret), asc=False))).items():
            if str(key).startswith('_') or not str(key).endswith('.type') or value != 'dict':
                continue
            
            item_master_key = Str.chop_end(key, '.type')
            item_is_sub = f'.{nest_key}.' in item_master_key
            item_nest_key = f'{item_master_key}.{nest_key}'
            is_item_nest_blank = Validate.blank(Data.get(ret, item_nest_key, {}))
            if not is_item_nest_blank:
                continue
            if item_is_sub:
                Data.forget(ret, item_master_key)
            else:
                Data.forget(ret, item_nest_key)
                Data.set(ret, f'{item_master_key}.required', False)
                Data.set(ret, f'{item_master_key}.default', {})
        
        if self.is_validation_ansible():
            return ret
        
        # remap = self.remappings()
        # for req_together in Data.get(ret, '_.required_together'):
        #     req_together = Helper.to_iterable(req_together)
        #     for req_key in req_together:
        #         deps = Data.get(ret, f'req_key.dependencies', [])
        #         deps.extend(req_together)
        #         Data.set(ret, f'req_key.dependencies', list(set(req_key) - set(deps)))

        # deps = Data.get(meta, '_.schema.url_username.dependencies', [])
        # deps.append('url_password')
        # Data.set(meta, '_.schema.url_username.dependencies', deps)
        # deps = Data.get(meta, '_.schema.url_password.dependencies', [])
        # deps.append('url_username')
        # Data.set(meta, '_.schema.url_password.dependencies', deps)

        
        return ret
    
    # def _cleanup_validation_schema_segments(self, ret: dict[str, str], segments: list[str]) -> dict:
    #     if Validate.blank(segments):
    #         return ret
        
    #     nest_key = self.get_validation_nest_key()
    #     cleanup = []
    #     for source in segments:
    #         if '.' not in source:
    #             cleanup.append(source)
    #             continue
            
    #         source_segments = source.split('.')

    #         if Validate.is_int_odd(len(source_segments)):
    #             source_segments = source_segments[:-1]
            
    #         cleanup.extend(map('.'.join, itertools.accumulate(itertools.batched(source_segments, n=2), lambda x, y: x + y)))

    #     cleanup = Data.dot_sort_keys(list(set(cleanup)), asc = False)

    #     for dest in cleanup:
    #         dest_master = Str.before_last(dest, '.')
    #         if Data.has(ret, dest) and Validate.blank(Data.get(ret, dest, {})):
    #             if dest.count('.') > 1:
    #                 Data.forget(ret, dest_master)
    #             else:
    #                 Data.forget(ret, dest)
    #                 if Data.has(ret, f'{dest_master}.required'):
    #                     Data.set(ret, f'{dest_master}.required', False)
    #                 if Data.has(ret, f'{dest_master}.default'):
    #                     Data.set(ret, f'{dest_master}.default', {})
    #                 if Data.has(ret, f'{dest_master}.options'):
    #                     Data.set(ret, f'{dest_master}.options', {})
        
    #     return ret
    
    def get_normalised_nested_key(self, key: str, ret: dict, only_base: bool = False) -> str:
        if '.' not in key:
            return key
        
        nest_key = self.get_validation_nest_key()
        ret = re.sub('\\.+', '.', key)
        
        # if only_base:
        #     return ret
        # elif self.is_validation_ansible():
        #     return ret.replace('.', f'.{nest_key}.')

        # return ret if only_base else 
        return ret
    
    def _prepare_validation_schema(self) -> dict:
        ret = {}
        
        for default_key, default_item in (self.cfg('defaults', {})).items():
            if default_key in (self.cfg('remap', {})).values():
                continue

            ret[default_key] = self._build_component_validation_schema(default_item)
        
        for segment in ['path', 'query', 'header', 'body', 'form']:
            ret[segment] = self._build_component_validation_schema({'type': 'object', 'required': False, 'default': {}}, require_props = False)

        return ret
    
    def _build_component_validation_schema(self, item: dict, **kwargs) -> dict:
        require_items = kwargs.pop('require_items', True)
        require_props = kwargs.pop('require_props', True)

        ret = {
            'type': item.get('type', ''),
            'required': item.get('required', False),
        }

        if Validate.filled(item.get('_validation', {})):
            ret = Data.combine(ret, item.get('_validation', {}), recursive = True)

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
        
        if Validate.filled(item.get('enum', {})):
            ret[self.get_validation_enum_key()] = item.get('enum', {}).copy()
        
        items_missing = require_items and ret['type'] == 'list' and Validate.blank(items_)
        props_missing = require_props and ret['type'] == 'dict' and Validate.blank(props_)
        if (items_missing or props_missing):
            self._error_value(f'Schema does not have children', ret)
        
        if ret['type'] not in ['list', 'dict']:
            return ret

        nest_key = self.get_validation_nest_key()
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
    
    def params(self, key: str  = '', default: Any = None) -> Any:
        return self._get_value(self._meta.get('params', {}), key, default)
    
    def meta(self, key: str  = '', default: Any = None) -> Any:
        return self._get_value(self._meta, key, default)
    
    def cfg(self, key: str  = '', default: Any = None) -> Any:
        return self._get_value(self._meta['cfg'], key, default)

    def cfg_has(self, key: str) -> bool:
        return Data.has(self._meta['cfg'], key)
    
    def params_set(self, params: Mapping) -> None:
        self._meta['params'] = dict(params).copy()
    
    def _handle_parameter_changes(self) -> None:
        
        path_file_cache = self.meta('_.path.file.cache')
        if Validate.file_exists(path_file_cache):
            cache = json.loads((lambda f: f.read())(open(path_file_cache)))
        else:
            cache = {'meta': {}, 'docs': {}}

        return
    
    def _handle_config_changes(self) -> None:
        from ansible.module_utils.basic import _load_params
        ansible_load_params = self.cfg('settings.ansible.load_params', False)
        if  ansible_load_params == True and not self.meta_has('_.params'):
            self.params_set(_load_params())
    
    def _save_cache(self, cache: Mapping):
        path_file_cache = self.meta('_.path.file.cache')
        if Validate.filled(path_file_cache):
            with open(path_file_cache, "w", encoding="utf-8") as f:
                json.dump(dict(cache), f, ensure_ascii=False)

    def swagger(self, key: str = '', default: Any = None) -> Any:
        return self._get_value(self._swagger, key, default)
    
    def _meta_set(self, key: str, value: Any) -> None:
        Data.set(self._meta, key, value)
    
    def _meta_forget(self, key: str) -> None:        
        Data.forget(self._meta, key)
    
    def meta_has(self, key: str) -> bool:
        return Data.has(self._meta, key)
    
    def is_validation_ansible(self):
        return self.cfg('settings.ansible.validation', False) == True
    
    def is_validation_cerberus(self):
        return not self.is_validation_ansible()
    
    def get_validation_type(self, type_: str, format_: str | None) -> str:
        if self.is_validation_cerberus():
            return self.get_cerberus_type(type_, format_)
        else:
            return self.get_ansible_type(type_)
    
    def get_validation_nest_key(self) -> str:
        return 'schema' if self.is_validation_cerberus() else 'options'
    
    def get_validation_enum_key(self) -> str:
        return 'allowed' if self.is_validation_cerberus() else 'choices'
    
    def _get_path_file_cache(self, path_tmp: str) -> str:
        filename = 'cache_tool_swagger.json'
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
    
    def load_swagger(self, source: Mapping | str, **kwargs) -> None:
        if Validate.is_mapping(source):
            swagger = dict(source) #type: ignore
        elif Validate.str_is_url(str(source)):
            kwargs = dict(kwargs)
            kwargs['url'] = str(source)
            swagger = json.loads(open_url(**kwargs).read().decode('utf-8'))
        elif Validate.file_exists(source):
            swagger = json.loads((lambda f: f.read())(open(str(source))))
        elif Validate.str_is_json(str(source)):
            swagger = json.loads(str(source))
        elif Validate.str_is_yaml(str(source)):
            swagger = yaml.safe_load(str(source))
        else:
            raise ValueError('Unable to identify swagger source type to load')
        
        self._meta_set('_.swagger_source', Str.to_md5(json.dumps(swagger)))
        self._meta_set('_.swagger_hash', Str.to_md5(json.dumps(swagger)))
        self._meta_set('_.swagger_timestamp', Helper.ts(mod = 'timestamp'))

        self._swagger = self.docs_extract(swagger, self.cfg('extraction', {}))