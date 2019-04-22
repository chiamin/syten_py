import sys, os
pylib = os.environ['SYTENDIRREAL']+'/pylib'
sys.path.append(pylib)
import pyten as p
from itertools import chain

def check_diff (A,B):
    a = A / p.tensor.norm(A)
    b = B / p.tensor.norm(B)
    return p.tensor.norm(a-b), p.tensor.norm(A)/p.tensor.norm(B)

def check_mpo (mpo, sites, length):
    tot_ratio = 1.
    for i in range(len(used_mpo)):
        diff, ratio = check_diff (mpo[i], used_mpo[i])
        if diff > 1e-12:
            print ('Error: MPO left side tensor does not match with used_mpo')
            raise Exception
        tot_ratio *= ratio
    for i in range (max(sites)+1, length):
        I = p.mp.genMPOId (mpo[i].getBasis(3), mpo[i].getBasis(1))
        diff, ratio = check_diff (I, mpo[i])
        if diff > 1e-12 or abs(ratio-1.) > 1e-12:
            print ('Error: MPO right side tensor is not proportional to identity')
            raise Exception
        tot_ratio *= ratio
    return tot_ratio

def pair_corr_mpo (lat,i,j,k,l):
    mpo = p.mp.dot(lat.get("c",i), lat.get("c",j)) * p.mp.dot(lat.get("c",k), lat.get("c",l))
    ratio = check_mpo (mpo, (i,j,k,l), lat.size())
    return mpo, ratio

def two_corr_mpo (lat,i,j):
    mpo = p.mp.dot(lat.get("c",i), lat.get("c",j))
    ratio = check_mpo (mpo, (i,j), lat.size())
    return mpo, ratio

# dummy left/right tensor on site i
def gen_left_dummy (mpo, mps, i):
    return p.tensor.genFuse (mpo[i].getBasis(2).flipped(),
                             mps.get_const(i).getBasis(2).flipped())

def gen_right_dummy (mpo, mps, i):
    return p.tensor.genSplit (mpo[i].getBasis(1).flipped(),
                              mps.get_const(i).getBasis(3).flipped())


def calc_contr_l(neigh, hcmp, mcmp):
    """Calculates a new left contraction component from the next left
contraction component in 'neigh', the local Hamiltonian component in
'hcmp' and the local MPS component in 'mcmp':

  [       ]-nl-[ mcmp ]-nr-
  [       ]        |       
  [       ]        t       
  [       ]        |       
  [ neigh ]-wl-[ hcmp ]-wr-
  [       ]        |       
  [       ]        s       
  [       ]        |       
  [       ]-ml-[ mcmp ]-mr-
    """
    #raise NotImplementedError("calc_contr_l() is not implemented yet!")
    ml = p.tensor.prod([1], neigh, mcmp, "wl,ml,nl|s,ml,mr|s,wl,mr,nl")
    mlw = p.tensor.prod([1,2], ml, hcmp, "s,wl,mr,nl|wr,wl,t,s|t,nl,wr,mr")
    return p.tensor.prod([1,2], mlw, mcmp, "t,nl,wr,mr|t,nl,nr|wr,mr,nr", True)

def set_sites_group (pcorr_str, pcorr_sites):
    # get the reference sites
    ref_sites = (pcorr_sites[0][0], pcorr_sites[0][2])
    right_corr, left_corr = [],[]
    for sites,pstr in zip(pcorr_sites, pcorr_str):
        # pair correlation
        if len(sites) == 4:
            # check the reference sites
            if sites[0] != ref_sites[0] or sites[2] != ref_sites[1]:
                print ('Reference sites not match')
                raise Exception
            if sites[1] > max(ref_sites) and sites[3] > max(ref_sites):
                right_corr.append ([pstr,sites])
            else:
                left_corr.append ([pstr,sites])
        elif len(sites) == 2:
            left_corr.append ([pstr,sites])

    right_corr = sorted (right_corr, key=lambda data: min([data[1][1],data[1][3]])) # sort by the 
    left_corr = sorted (left_corr, key=lambda data: min(data[1]))

    return ref_sites, right_corr, left_corr

def push_L_right (L, iL, i, mpo, mps):
# Contract L from site iL to i-1
    for j in range(iL,i):
        L = calc_contr_l (L, mpo[j], mps.get_const(j))
        iL = j+1
        mps.maybeCache (j)

        if j != len(used_mpo):
            print ('Error: check mpo', len(used_mpo), j)
            raise Exception
        used_mpo.append (mpo[j])
    return L, iL

def compute_expectation (L, iL, iend, mpo, mps):
# will NOT change L outside
    for j in range(iL,iend+1):
        L = calc_contr_l (L, mpo[j], mps.get_const(j))
    R = gen_right_dummy (mpo, mps, iend)
    val = p.tensor.prod([1,2,3], L, R, False).real
    return val

def get_argv (key, typ=str, default=None, verbose=True):
    for arg in sys.argv:
        if key in arg and '=' in arg:
            tmp = arg.split('=')[-1]
            if verbose: print ('get',key,'=',tmp, flush=True)
            return typ(tmp)
    print ('get default value =',default, flush=True)
    return default

def print_pair_corr (pstr, val, out_file=''):
    if out_file != '':
        print (pstr, val, file=open(out_file, "a"), flush=True)
    else:
        print (pstr, val, flush=True)

if __name__ == '__main__':
    cache_threshold = get_argv('cache-threshold',int,1048576)
    lat_file = get_argv('lat')
    psi_file = get_argv('psi')
    mea_file = get_argv('mea')
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

    # Read measurement template file
    print ('Organizing correlation sites')
    pcorr_str, pcorr_sites = [],[]
    with open(mea_file) as f:
        for line in f:
            tmp = line.split('=')[-1].split()[0]
            tmp = list(map(int,tmp.split(',')))
            pcorr_sites.append (tmp)
            pcorr_str.append (line.split()[0])
    ref_sites, right_corr, left_corr = set_sites_group (pcorr_str, pcorr_sites)

    # Initialize left tensor L
    # iL is the next right site
    mpo, ratio = pair_corr_mpo (lat, *pcorr_sites[0])
    L = gen_left_dummy (mpo, psi, 0)
    iL = 0

    i_progress = 1
    # left_corr
    for pstr,sites in left_corr:
        print ('working on',i_progress,'/',len(pcorr_sites), flush=True)
        i_progress += 1

        if len(sites) == 4:
            mpo, ratio = pair_corr_mpo (lat, *sites)
        elif len(sites) == 2:
            mpo, ratio = two_corr_mpo (lat, *sites)
        i, iend = min(sites), max(sites)
        L, iL = push_L_right (L, iL, i, mpo, psi)
        val = compute_expectation (L, iL, iend, mpo, psi)
        val *= ratio
        print_pair_corr (pstr, val, out_file)

    # right_corr
    for pstr,sites in right_corr:
        print ('working on',i_progress,'/',len(pcorr_sites), flush=True)
        i_progress += 1

        mpo, ratio = pair_corr_mpo (lat, *sites)
        run_sites = [sites[1],sites[3]]
        i, iend = min(run_sites), max(run_sites)
        L, iL = push_L_right (L, iL, i, mpo, psi)
        val = compute_expectation (L, iL, iend, mpo, psi)
        print_pair_corr (pstr, val, out_file)

