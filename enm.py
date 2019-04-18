import sys
from discwt import getdata_full, takedata_eachm
import pylab as pl


def takedata_fromm (dat, ms, mmin=0):
    ibeg = 0
    for i in xrange(len(ms)):
        if ms[i] >= mmin:
            ibeg = i
            break
    re = [di[ibeg:] for di in dat]
    return re

if __name__ == '__main__':
    fname = sys.argv[1]
    mmin = 0
    if '-minm' in sys.argv:
        mmin = int(sys.argv[sys.argv.index('-minm')+1])

    its,ns,ens,enps,terrs,ms,msu2s,clocks,cputimes = getdata_full (fname)
    its,ns,ens,enps,terrs,ms,msu2s,clocks,cputimes = takedata_fromm ((its,ns,ens,enps,terrs,ms,msu2s,clocks,cputimes), ms, mmin=mmin)
    its1,ns1,ens1,enps1,terrs1,ms1,msu2s1,clocks1,cputimes1 = takedata_eachm ((its,ns,ens,enps,terrs,ms,msu2s,clocks,cputimes), ns, ms)

    fig, ax1 = pl.subplots()
    ax1.plot (its,enps,'o-k')
    ax1.set_xticks (its1)
    ax1.set_xticklabels (ms1)
    #ax1.set_xlabel ('half-sweep iteration',fontsize=18)
    ax1.set_xlabel ('bond dimension',fontsize=18)
    ax1.set_ylabel ('energy per site',fontsize=18)

    #ax2 = ax1.twinx()
    #ax2.plot (its,ms,'x-r')
    #ax2.set_yticks (ms1)
    #ax2.set_ylabel ('bond dimension',fontsize=18,color='r')

    pl.show()
