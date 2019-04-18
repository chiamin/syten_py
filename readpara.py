
def search_after (fname, must, key):
    f = open (fname)
    for line in f:
        if must in line:
            tmp = line.split()
            ind = tmp.index(key)
            re = tmp[ind+1]
            return re

def get_flag (writeM=1048576,cpus_dense=1,cpus_tensor=1,cpus_super=1):
    flag =  ' --cache --cache-threshold '+str(writeM)+' '
    flag += ' --threads-dense '+str(cpus_dense)+' '
    flag += ' --threads-tensor '+str(cpus_tensor)+' '
    flag += ' --threads-super '+str(cpus_super)+' '
    return flag

def read_arg (argv,keys):
    try: len(keys)
    except: keys = [keys]

    opts = []
    for key in keys:
        x = '-'+key
        if x in argv:
            opt = argv[argv.index(x)+1]
            opts.append (opt)
    return opts

def read_arg_dict (argv, keys, para=dict()):
    try: len(keys)
    except: keys = [keys]

    for key in keys:
        x = '-'+key
        if x in argv:
            para[key] = argv[argv.index(x)+1]
    return para

def read_lat (fname):
    f = open (fname)
    for line in f:
        if 'syten-dmrg' in line:
            tmp = line.split()
            ind = tmp.index('-l')
            lat = tmp[ind+1].split(':')[0]
            return lat
    print 'Cannot find lattice'
    raise Exception

def read_para (fname, keys, typ, sp='=', default=[]):
    if type(keys) == str:
        keys = [keys]
        default = [default]
    #if type(default) != list: default = [default]
    para = []
    for i in xrange(len(keys)):#key in keys:
        key = keys[i]
        f = open (fname)
        for line in f:
            if key in line:
                tmp = line.split(sp)
                if len(tmp) >= 2 and tmp[0].strip() == key:
                    name = para.append (typ(line.split()[-1]))
                    break
        else:
            if len(default) != 0:
                para.append (typ(default[i]))
            else:
                print 'Cannot find',key,'in',fname
                raise KeyError
        f.close()
    if len(para) == 1: para = para[0]
    return para

def read_para_dict (fname, keys, typ, sp='=', default=[], para=dict()):
    plist = read_para (fname, keys, typ, sp, default)
    for key,par in zip(keys,plist):
        para[key] = par
    return para

def to_float_or_int_or_str (x):
    try:
        x = float(x)
        if x.is_integer():
            return int(x)
        else:
            return x
    except:
        return str(x)

def to_var_or_list (string):
    x = string.split()
    if len(x) == 1:
        return to_float_or_int_or_str (x[0])
    else:
        return map(to_float_or_int_or_str, x)

def read_block (fname, blockname, sp='='):
    f = open(fname)
    for line in f:
        if line.strip() == blockname: break
    para = dict()
    for line in f:
        if '}' in line:
            return para
        tmp = line.split ('=')
        if len(tmp) == 2:
            para[tmp[0].strip()] = to_var_or_list (tmp[1])
    return para

def read_block_terms (fname, blockname, keys):
    f = open(fname)
    for line in f:
        if line.strip() == blockname: break
    for line in f:
        if all(x in line for x in keys): break
    para = []
    for line in f:
        if '}' in line: return para
        tmp = line.split()
        para.append (map(to_float_or_int_or_str,tmp))
    return para

def read_Npar (fname):
    lx,ly = read_para (fname, ('lx','ly'), int, '=')
    f = open (fname)
    for line in f:
        if 'Npar' in line and '=' in line:
            if '(' in line:
                tmp = line.split()[-1]
                tmp = tmp.lstrip('(')
                tmp = tmp.rstrip(')')
                tmp = tmp.split('/')
                nume,deno = map(int,tmp)
                Npar = lx*ly*nume/deno
            else:
                Npar = int(line.split()[-1])
            return Npar
    print 'Cannot read Npar'
    raise Exception
