import typing as t
### BEGIN: ImportManager
### END: ImportManager

def ts(**kwargs):
    import datetime
    ts = datetime.datetime.now(datetime.timezone.utc)
    mod = kwargs.pop('mod', '')
    
    if Validate_filled(mod):
        return Convert_as_ts_mod(ts, mod)

    return ts

def timestamp(**kwargs):
    return ts(**kwargs)

def random_string(length: PositiveInt = 32)-> str:
    import random, string
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))

### BEGIN: FS
def fs_path_tmp(file: str, *args, **kwargs)-> str:
    import tempfile
    is_dir = kwargs.pop('dir', False)
    args = list(args)
    ensure_directory_exists = is_dir or len(args) > 1
    args = [tempfile.gettempdir()] + args + [file]
    ret = Utils_fs_join_paths(*args)
    
    if ensure_directory_exists:
        path_dir = ret if is_dir else Utils_fs_dirname(ret)
        Utils_fs_ensure_directory_exists(path_dir)
    
    return ret
### END: FS

### BEGIN: Play
def play_meta(vars: t.Mapping, **kwargs)-> dict:
    import urllib, urllib.parse
    make_cache = kwargs.pop('make_cache', False)
    ts_ = ts()

    play_hosts = ','.join(vars.get('ansible_play_hosts_all', []))
    play_batch = ','.join(vars.get('ansible_play_batch', []))
    ret = {
        'ph': 'N/A' if Validate_blank(play_hosts) else play_hosts,
        'if': vars.get('inventory_file', 'N/A'),
        'cf': vars.get('ansible_config_file', 'N/A'),
        'pbd': vars.get('playbook_dir', 'N/A'),
        'pbn': vars.get('ansible_play_name', 'N/A'),
        'pb': 'N/A' if Validate_blank(play_batch) else play_batch,
        'ts': Convert_as_ts_mod(ts_, 'long_safe'), #type: ignore
    }

    kwargs['encoding'] = kwargs.get('encoding', 'utf-8')
    play_id = Convert_to_url_encode(ret, **kwargs)
    play_id = urllib.parse.unquote(play_id, encoding='utf-8', errors='strict')
    ret = {
        'id': {
            'raw': play_id,
            'hash': Convert_to_md5(play_id),
        },
        'ts': {
            'raw': ts_,
            'str': Convert_as_ts_mod(ts_, 'str'), #type: ignore
            'safe': Convert_as_ts_mod(ts_, 'safe'), #type: ignore
            'long': Convert_as_ts_mod(ts_, 'long'), #type: ignore
            'long_safe': Convert_as_ts_mod(ts_, 'long_safe'), #type: ignore
            'timestamp': Convert_as_ts_mod(ts_, 'timestamp'), #type: ignore
        },
        'placeholder': placeholder(mod='hash'),
        'cache_file': fs_path_tmp(f'play_{Convert_to_md5(play_id)}.json'),
    }

    if make_cache and not Validate_fs_file_exists(ret['cache_file']):
        cache_defaults = kwargs.pop('cache_defaults', {})
        cache_content = Data_combine(cache_defaults, {'play': Convert_as_copied(ret)}, recursive=True)
        Utils_json_save(cache_content, ret['cache_file'])

    return ret
### END: Play

### BEGIN: Net
def net_random_mac(value: str, seed=None):
    import re
    value = value.lower()
    mac_items = value.split(':')

    if len(mac_items) > 5:
        raise ValueError(f'Invalid value ({value}) for random_mac: 5 colon(:) separated items max')

    err = ""
    for mac in mac_items:
        if not mac:
            err += ",empty item"
            continue
        if not re.match('[a-f0-9]{2}', mac):
            err += f",{mac} not hexa byte"
    err = err.strip(',')

    if err:
        raise ValueError(f'Invalid value ({value}) for random_mac: {err}')

    from random import Random, SystemRandom
    if seed is None:
        r = SystemRandom()
    else:
        r = Random(seed)
    
    v = r.randint(68719476736, 1099511627775)
    remain = 2 * (6 - len(mac_items))
    rnd = f'{v:x}'[:remain]
    return value + re.sub(r'(..)', r':\1', rnd)
### END: Net