import sys, os
pylib = os.environ['SYTENDIRREAL']+'/pylib'
sys.path.append(pylib)
import pyten as p

def check_diff (A,B):
    a = A / p.tensor.norm(A)
    b = B / p.tensor.norm(B)
    return p.tensor.norm(a-b), p.tensor.norm(A)/p.tensor.norm(B)

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
    re = p.tensor.prod([1,2], mlw, mcmp, "t,nl,wr,mr|t,nl,nr|wr,mr,nr", True)
    return re

def calc_contr_r(neigh, hcmp, mcmp):
    """Calculates a new right contraction component from the next right
contraction component in 'neigh', the local Hamiltonian component in
'hcmp' and the local MPS component in 'mcmp':

  -nl-[ mcmp ]-nr-[       ]
          |       [       ]
          t       [       ]
          |       [       ]
  -wl-[ hcmp ]-wr-[ neigh ]
          |       [       ]
          s       [       ]
          |       [       ]
  -ml-[ mcmp ]-mr-[       ]

    """
    mr = p.tensor.prod([1], neigh, mcmp, "wr,mr,nr|s,ml,mr|s,wr,ml,nr")
    mrw = p.tensor.prod([1,2], mr, hcmp, "s,wr,ml,nr|wr,wl,t,s|t,nr,wl,ml")
    return p.tensor.prod([1,2], mrw, mcmp, "t,nr,wl,ml|t,nl,nr|wl,ml,nl", True)

def check_mpo_identity (mpo, ibeg, iend1):
# Check the MPO tensors equal to the identity tensor for the site from ibeg to iend
# iend1 = the last site to be checked + 1
# i_not_id_end is the last site that mpo[i] is not identity
    tot_ratio = 1.
    i_not_id_end = ibeg-1
    for i in range (ibeg, iend1):
        I = p.mp.genMPOId (mpo[i].getBasis(3), mpo[i].getBasis(1))
        diff, ratio = check_diff (I, mpo[i])
        if diff > 1e-12:
            i_not_id_end = i
            tot_ratio = 1.
            print ('>',i,ratio,tot_ratio)
        else:
            tot_ratio *= ratio
            print ('<',i,ratio,tot_ratio,mpo.size())
    return tot_ratio, i_not_id_end

class CheckTensorSame:
    def __init__ (self,N):
        self.tensor = [None for i in range(N)]
    def set (self, i, tensor):
        self.tensor[i] = tensor
    def check (self, i1, iend, mpo):
        tot_ratio = 1.
        for i in range(i1,iend):
            diff, ratio = check_diff (self.tensor[i], mpo[i])
            if diff > 1e-12:
                print ('Error: MPO tensor does not match with self.tensor')
                print ('i=',i,'diff=',diff)
                raise Exception
            tot_ratio *= ratio
        return tot_ratio
            
class LeftTensor:
    def __init__ (self, mpo, mps):
        self.i = 0
        self.tensor = gen_left_dummy (mpo, mps, 0)
        self.mpo_left = []
        self.check_mpo = CheckTensorSame (mpo.size())

    def push_right (self, i, mpo, mps):
    # Contract L from site self.i to i-1
        if i < self.i:
            print ('i < self.i',i,self.i)
            raise IndexError
        for j in range(self.i,i):
            self.tensor = calc_contr_l (self.tensor, mpo[j], mps.get_const(j))
            self.i = j+1
            mps.maybeCache (j)
            check_mpo.set (j, mpo[j])

    def check_mpo_left (self, mpo):
    # Check the new MPO has the same tensors with the contracted MPO tensors for i=0 to i=self.i-1
        tot_ratio = 1.
        return self.check_mpo.check (0, self.i, mpo)

def right_tensors (mpo, mps):
    Rs = [None for i in range(mpo.size())]
    Rs[-1] = gen_right_dummy (mpo, mps, mps.size()-1)
    for i in range(mps.size()-2,-1,-1):
        R = calc_contr_r (Rs[i+1], mpo[i+1], mps.get_const(i+1))
        Rs[i] = R
    return Rs

class GenRightTensor:
    def __init__ (self, mpo, mps):
        self.Rs0 = right_tensors (mpo, mps)
        self.mpo0 = mpo
        self.mps = mps

    def compute_R (self, mpo, i1):
        R = self.Rs0[-1]
        # Get the iR, where for i>iR, the mpo[i]==mpo0[i], and thus Rs[i-1]==Rs0[i-1]
        for i in range(self.mps.size()-2,i1-1,-1):
            diff, ratio = check_diff (self.mpo0[i+1], mpo[i+1])
            if diff < 1e-12:
                iR = i
                R = self.Rs0[i]
            else:
                iR = i+1
                break
        # Compute Rs for i1<=i<=iR-1
        for i in range(iR,i1,-1):
            R = calc_contr_r (R, mpo[i], self.mps.get_const(i))
        return R

def sort_objs (iss, objs):
# <iss> = [[i1,i2,...],[j1,j2,...],...]
# sort <objs> by {min(<iss>[i])}
# len(iss) should equals to len(objs)
    if len(iss) != len(objs):
        print ('length not match')
        raise IndexError
    imins = [min(i) for i in iss]
    sorted_tmp = sorted (zip(imins,iss,objs))
    min_iss, sorted_iss, sorted_objs = list(zip(*sorted_tmp))
    return sorted_iss, sorted_objs

def compute_expectation_L (LE:LeftTensor, iend, mpo, mps, R=None):
# Compute the expectation value for MPO from L.i to iend
# Will NOT change the L outside
    L = LE.tensor
    for j in range(LE.i,iend+1):
        L = calc_contr_l (L, mpo[j], mps.get_const(j))
    if R == None:
        R = gen_right_dummy (mpo, mps, iend)
    val = p.tensor.prod([1,2,3], L, R, False).real
    return val

def compute_expectation (mpo, mps):
    LE = LeftTensor (mpo, mps)
    return compute_expectation_L (LE, mps.size()-1, mpo, mps)

def compute_expectations (indss, mpos, mps, cache_threshold=1048576,threads_tensor=1,threads_dense=1):
# Compute the expecation values for all the MPO in <mpos>
# <indss> contains the indices of each MPO in <mpos>
# For example, for mpos[0], indss[0]=[i1,i2,i3], which means that mpos[0] spans only between min(indss[0]) and max(indss[0])
    p.setCacheThreshold (cache_threshold)
    p.threading.setTensorNum (threads_tensor)
    p.threading.setDenseNum (threads_dense)

    indss, mpos = sort_objs (indss, mpos)
    LE = LeftTensor (mpos[0], mps)
    RGen = GenRightTensor (mpos[0], mps)

    vals = []
    for inds, mpo in zip(indss, mpos):
        print ('working on indices:',*inds)
        ibeg = min(inds)
        iend = max(inds)

        R = RGen.compute_R (mpo, iend)

        val = compute_expectation_L (LE, iend, mpo, mps, R)
        # Check the left tensors for i<LE.i are proportional to the previous tensors absorted in LE
        ratio_l = LE.check_mpo_left (mpo)

        vals.append (ratio_l * val)

    return vals
