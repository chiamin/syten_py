import sys, glob
import pylab as pl
sys.path.append ('/home/chiamin/mypy')
from fitfun import myfit
from readpara import read_para

def getdata_half_sweep (f,N):
    ns,ens,terrs,ms,msu2s,wallclocks,cputimes = [],[],[],[],[],[],[]
    swp = 0
    good = False
    for line in f:
            #if 'Done DMRG' in line: break

            tmp = line.split()

            if len(tmp) != 19:
                print 'Error: line pattern not match. Current line:'
                print line
                break
                #raise Exception

            swpt  = int(tmp[5])
            if swp != 0 and swp != swpt:
                good = True
                break
            swp = swpt

            n    = int(tmp[4])
            en   = float(tmp[7])
            terr = float(tmp[11])
            m    = int(tmp[15])
            msu2 = int(tmp[16])
            wallclock = tmp[0]
            cputime = float(tmp[1])

            ns.append(n)
            ens.append(en)
            terrs.append(terr)
            ms.append(m)
            msu2s.append(msu2)
            wallclocks.append(wallclock)
            cputimes.append(cputime)

            if len(ns) == N-1:
                good = True
                break

    return ns,ens,terrs,ms,msu2s,good,wallclocks,cputimes


def getdata_full (fname):
    lx,ly = read_para (fname, ('lx','ly'), int, '=')

    f = open (fname)
    for line in f:
        if 'lx' in line: lx = int(line.split()[-1])
        if 'ly' in line:
            ly = int(line.split()[-1])
            break
    f.close()
    size = lx*ly

    f = open (fname)
    for line in f:
        if 'D Stg. Swp.  #Pos' in line: break
    nss,enss,enps,terrss,mss,msu2ss,clocks,cputimes,good = [],[],[],[],[],[],[],[],True
    while good:
        ns,ens,terrs,ms,msu2s,good,wallclock,cputime = getdata_half_sweep (f,lx*ly)
        if not good: break
        nss.append (ns[-1])
        enss.append (ens[-1])
        terrss.append (sum(terrs)/len(terrs))
        mss.append (max(ms))
        msu2ss.append (max(msu2s))
        enps.append (ens[-1]/size)
        clocks.append (wallclock[-1])
        cputimes.append (cputime[-1])
    its = range(len(nss))
    return its,nss,enss,enps,terrss,mss,msu2ss,clocks,cputimes

def takedata_eachm (dat, ns, ms, mmin=0, mmax=1000000):
    # get the index for the last data in each m
    ii = []
    reach_maxm = False
    for i in xrange(len(ns)):
        m = ms[i]
        if m >= mmin and m <= mmax and (i == len(ns)-1 or ns[i] != ns[i+1]):
            if m <= mmax: reach_maxm = True
            ii.append (i)
    if len(ii) == 0:
        print 'minm is too big'
        print 'ms =',ms
        print 'minm =',mmin
        raise Exception
    if ii[-1] != ns[-1] and not reach_maxm:
        ii.append (len(ns)-1)

    re = []
    for i in xrange(len(dat)):
        re.append ([dat[i][j] for j in ii])
    return re

def get_var (fname):
    varis,ns = [],[]
    with open(fname) as f:
        for line in f:
            if '.state' in line:
                n = int(line.split('_')[-2])
            if 'up-to-two-site' in line:
                var = float(line.split()[-1])
                ns.append (n)
                varis.append (var)
    return ns, varis

def get_data (fname, mmin=64, var_file='', mmax=1000000,detail=False,verbose=True):
    its,ns,ens,enps,terrs,ms,msu2s,clocks,cputimes = getdata_full (fname)

    if verbose:
        print 'n E E/N TruncErr m m(SU2)'
        for i,j,k,p,q,r in zip(ns,ens,enps,terrs,ms,msu2s): print i,j,k,p,q,r

    if detail:
        xx = range(len(ns))
        f,ax = pl.subplots()
        ax.plot (xx,enps,marker='o')
        ax.set_ylabel('E',fontsize=16)
        ax2 = ax.twinx()    
        ax2.plot (xx,ms,c='k')
        ax2.set_ylabel('m',fontsize=16)
        pl.show()

    ns,ens,enps,terrs,ms,msu2s = takedata_eachm ((ns,ens,enps,terrs,ms,msu2s), ns, ms, mmin, mmax)
    if verbose:
        print
        print 'n E E/N TruncErr m m(SU2)'
        for i,j,k,p,q,r in zip(ns,ens,enps,terrs,ms,msu2s): print i,j,k,p,q,r

    if var_file != '':
        lx,ly = read_para (fname, ('lx','ly'), int, '=')
        ns_var, var = get_var (var_file)
        ind = ns_var.index(ns[0])
        ns_var = ns_var[ind:]
        var = [i/(lx*ly)**2 for i in var[ind:]]

        if verbose:
            print '\nn en_var'
            for i,j in zip(ns_var,var): print i,j

        ilast = 0
        for n in ns_var:
            if n in ns:
                ilast += 1

        terrs = var[:ilast]
        ens = ens[:ilast]
        enps = enps[:ilast]
        ns = ns[:ilast]
        ms = ms[:ilast]
        msu2s = msu2s[:ilast]

    return terrs, ens, enps, ns, ms, msu2s

def get_en_extrap (fname, mmin=64, var_file='', mmax=1000000,detail=False,verbose=True, fitn=0, ax=None, plot=True, fitorder=1):
    terrs, ens, enps, ns, ms, msu2s = get_data (fname, mmin, var_file, mmax, detail, verbose)

    if fitn != 0:
        terrs = terrs[-fitn:]
        enps  = enps[-fitn:]
    if ax == None and plot:
        f,ax = pl.subplots()

    fitx, fity, stddev = myfit (terrs, enps, werr=terrs, ax=ax, order=fitorder, pltargs={'c':'k','marker':'None'})
    if plot and ax != None:
        ax.plot (terrs, enps, 'ok')
        if var_file == '': xlabel = 'Truncation error'
        else: xlabel = '(two-site) energy variance'
        pl.xlabel (xlabel,fontsize=16)
        pl.ylabel ('energy per site',fontsize=16)
        pl.tight_layout()

    en, err = fity[-1], 0.2*abs(fity[-1]-enps[-1])
    return en, err

if __name__ == '__main__':
    if '-auto' in sys.argv:
        fname = glob.glob("*.out")[0]
    else:
        fname = sys.argv[1]
    mmin,mmax = 64,1000000
    var_file = ''
    fitn = 0
    detail = False
    fitorder = 1
    if '-minm' in sys.argv:
        mmin = int(sys.argv[sys.argv.index('-minm')+1])
    if '-maxm' in sys.argv:
        mmax = int(sys.argv[sys.argv.index('-maxm')+1])
    if '-var' in sys.argv:
        if '-auto' in sys.argv:
            var_file = glob.glob("*.variance")[0]
        else:
            var_file = sys.argv[sys.argv.index('-var')+1]
    if '-fitn' in sys.argv:
        fitn = int(sys.argv[sys.argv.index('-fitn')+1])
    if '-detail' in sys.argv:
        detail = True
    if '-order' in sys.argv:
        fitorder = int(sys.argv[sys.argv.index('-order')+1])

    print 'maxm =',mmax

    terrs, ens, enps, ns, ms, msu2s = get_data (fname, mmin, var_file, mmax=mmax,detail=detail)

    print ms
    print enps

    if fitn != 0:
        terrs = terrs[-fitn:]
        enps  = enps[-fitn:]

    f,ax = pl.subplots()
    ax.plot (terrs, enps, 'ok')
    fitx, fity, stddev = myfit (terrs, enps, werr=terrs, ax=ax, order=fitorder, pltargs={'c':'k','marker':'None'})
    if var_file == '': xlabel = 'Truncation error'
    else: xlabel = '(two-site) energy variance'
    pl.xlabel (xlabel,fontsize=16)
    pl.ylabel ('energy per site',fontsize=16)
    pl.tight_layout()
    if '-pdf' in sys.argv:
        pl.savefig (fname+'_en_truncerr.pdf')

    print '\nfitted points:'
    print 'n  trunerr  en_per_site  ms  msu2s'
    for n,te,tot_en,en,m,msu2 in zip(ns,terrs,ens,enps,ms,msu2s): print n,'  ',te,'  ',tot_en,'  ',en,'  ',m,'  ',msu2
    print '\nenergy per site =',fity[-1],'+-',0.2*abs(fity[-1]-enps[-1]),'(stddev='+str(stddev)+')'

    pl.show()
