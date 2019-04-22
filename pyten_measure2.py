import sys, os
pylib = os.environ['SYTENDIRREAL']+'/pylib'
sys.path.append(pylib)
import pyten as p

# dummy left/right tensor on site i
def gen_left_dummy (mpo, mps, i):
    return p.tensor.genFuse (mpo[i].getBasis(2).flipped(),
                             mps.get_const(i).getBasis(2).flipped())

def gen_right_dummy (mpo, mps, i):
    return p.tensor.genSplit (mpo[i].getBasis(1).flipped(),
                              mps.get_const(i).getBasis(3).flipped())

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

def left_tensors (mpo, mps):
    LEs = [gen_left_dummy (mpo, mps, 0)]
    for i in range(1,len(mpo)):
        LE = calc_contr_l (LEs[i-1], mpo[i], mps.get_const(i))
        LEs.append (LE)
    return LEs

def right_tensors (mpo, mps):
    REs = [gen_right_dummy (mpo, mps, mps.size()-1)]
    for i in range(mps.size()-2,-1,-1):
        RE = calc_contr_r (REs[i+1], mpo[i], mps.get_const(i))
        REs.append (RE)
    return REs

