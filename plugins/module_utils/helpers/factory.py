from ansible_collections.aybarsm.utils.plugins.module_utils.helpers.aggregator import (
    __convert, __validate
)

def ts(**kwargs):
    import datetime
    ts = datetime.datetime.now(datetime.timezone.utc)
    mod = kwargs.pop('mod', '')
    
    if __validate().filled(mod):
        return __convert().as_ts_mod(ts, mod)
    
    return ts

def random_string(length: int = 32)-> str:
    import random, string
    return ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(length))

def placeholder(rand_length: int = 32, mod: str = ''):
    import math
    ret = [
        random_string(math.ceil(rand_length/2)),
        ts(mod='long'),
        random_string(math.floor(rand_length/2))
    ]

    ret = '|'.join(ret)
    
    mod = mod.lower()
    if mod in ['hash', 'hashed']:
        return __convert().to_md5(ret)
    else:
        return ret