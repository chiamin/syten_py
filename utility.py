import sys

def get_argv (key, typ=str, default=None, verbose=True):
    for arg in sys.argv:
        if key in arg and '=' in arg:
            tmp = arg.split('=')[-1]
            if verbose: print ('get',key,'=',tmp, flush=True)
            return typ(tmp)
    print ('get default value =',default, flush=True)
    return default
