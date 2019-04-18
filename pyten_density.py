import sys, os
pylib = os.environ['SYTENDIRREAL']+'/pylib'
sys.path.append(pylib)
import pyten as p
from itertools import chain

# dummy left/right tensor on site i
def gen_left_dummy (mps, i):
    return p.tensor.genFuse (mps.get_const(i).getBasis(2).flipped())

def gen_right_dummy (mps, i):
    return p.tensor.genSplit (mps.get_const(i).getBasis(3).flipped())


def calc_contr_l (neigh, mcmp, ni):
    """
  [       ]-nl-[ mcmp ]-nr-
  [       ]        |       
  [       ]        |       
  [       ]        |       
  [ neigh ]        t
  [       ]        |       
  [       ]        |       
  [       ]        |       
  [       ]-ml-[ mcmp ]-mr-
    """
    # local n * A
    nA = p.tensor.prod([1], ni, mcmp, "s,t|s,ml,mr|t,ml,nr")

    if neigh == None:
        L = p.tensor.prod([1], mcmp, mcmp, "t,ml,mr|t,ml,nr|mr,nr", True)
        n = p.tensor.prod([1,2,3], mcmp, nA, True).real
    else:
        ml = p.tensor.prod([1], neigh, mcmp, "ml,nl|t,ml,mr|t,mr,nl")
        L = p.tensor.prod([1], ml, mcmp, "t,mr,nl|t,nl,nr|mr,nr", True)
        n = p.tensor.prod([1,2,3], ml, nA, True).real

    return L, n

def get_argv (key, typ=str, default=None, verbose=True):
    for arg in sys.argv:
        if key in arg and '=' in arg:
            tmp = arg.split('=')[-1]
            if verbose: print ('get',key,'=',tmp, flush=True)
            return typ(tmp)
    print ('get default value =',default, flush=True)
    return default

if __name__ == '__main__':
    cache_threshold = get_argv('cache-threshold',int,1048576)
    lat_file = get_argv('lat')
    psi_file = get_argv('psi')
    out_file = get_argv('out',default='')
    threads_tensor = get_argv('threads-tensor',int,1)
    threads_dense = get_argv('threads-dense',int,1)

    p.setCacheThreshold (cache_threshold)
    p.threading.setTensorNum (threads_tensor)
    p.threading.setDenseNum (threads_dense)

    used_mpo = []

    print ('Loading lattice',lat_file)
    lat = p.mp.Lattice (lat_file)
    print ('Loading MPS',psi_file)
    psi = p.mp.MPS()
    psi.setMaybeCache (True)
    psi.load (psi_file)
    #psi = p.mp.MPS (psi_file)

    N = lat.size()
    L = None
    for i in range(1,N+1):
        ni_op = lat.get('n',i)
        L, ni = calc_contr_l (L, psi.get_const(i), ni_op)
        print (i, ni)

