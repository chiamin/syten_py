import sys
import pylab as pl
sys.path.append ('/home/chiamin/mypy')
from fitfun import myfit

def getdata_half_sweep (f):
    ns,ens,terrs,ms,msu2s,wallclocks,cputimes = [],[],[],[],[],[],[]
    good = False
    for line in f:
            if 'Starting' in line and 'left' in line and 'right' in line: break
    for line in f:
            if 'Timing information' in line:
                good = True
                break
            if 'Attempting to use dgesvd' in line: continue

            tmp = line.split()
            if len(tmp) != 19:
                print 'gg',line
                good = False
                break
            n    = int(tmp[4])
            en   = float(tmp[7])
            terr = float(tmp[11])
            m    = int(tmp[15])
            msu2 = int(tmp[16])
            wallclock = tmp[0]
            cputime = float(tmp[1])

            #print n,m
            #print line

            ns.append(n)
            ens.append(en)
            terrs.append(terr)
            ms.append(m)
            msu2s.append(msu2)
            wallclocks.append(wallclock)
            cputimes.append(cputime)
    return ns,ens,terrs,ms,msu2s,good,wallclocks,cputimes

def getdata_full (fname):
    with open (fname) as f:
        for line in f:
            if 'lx' in line: lx = int(line.split()[-1])
            if 'ly' in line:
                ly = int(line.split()[-1])
                break
    size = lx*ly

    nss,enss,enps,terrss,mss,msu2ss,clocks,cputimes = [],[],[],[],[],[],[],[]
    with open(fname) as f:
        npre = count = 0
        terr = 0.
        for line in f:
            if not line[0].isdigit(): continue
            if line == '\n': continue

            tmp = line.split()
            if len(tmp) != 19: continue
            if line.strip()[-3:] == 'son': continue

            count += 1
            n    = int(tmp[4])
            en   = float(tmp[7])
            terr += float(tmp[11])
            m = int(tmp[15])
            msu2 = int(tmp[16])
            wallclock = tmp[0]
            cputime = float(tmp[1])

            if n != npre:
                for i in [nss,enss,enps,terrss,mss,msu2ss,clocks,cputimes]:
                    i.append(None)

            nss[-1] = n
            enss[-1] = en
            enps[-1] = en/size
            terrss[-1] = terr/count
            if m > mss[-1]: mss[-1] = m
            if msu2 > msu2ss[-1]: msu2ss[-1] = msu2
            clocks[-1] = wallclock
            cputimes[-1] = cputime

            if n != npre:
                count = 0
                terr = 0.
                npre = n

    its = range(len(nss))
    return its,nss,enss,enps,terrss,mss,msu2ss,clocks,cputimes


'''def getdata_full (fname):
    f = open (fname)
    for line in f:
        if 'lx' in line: lx = int(line.split()[-1])
        if 'ly' in line:
            ly = int(line.split()[-1])
            break
    f.close()
    size = lx*ly

    f = open (fname)
    nss,enss,enps,terrss,mss,msu2ss,clocks,cputimes,good = [],[],[],[],[],[],[],[],True
    while good:
        ns,ens,terrs,ms,msu2s,good,wallclock,cputime = getdata_half_sweep (f)
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
    return its,nss,enss,enps,terrss,mss,msu2ss,clocks,cputimes'''

def takedata_eachm (dat, ns, ms, mmin=0):
    # get the index for the last data in each m
    ii = []
    for i in xrange(len(ns)):
        m = ms[i]
        if m >= mmin and i != len(ns)-1 and ns[i] != ns[i+1]:
            ii.append (i)
    if len(ii) == 0:
        print 'minm is too big'
        print 'ms =',ms
        print 'minm =',mmin
        raise Exception
    if ii[-1] != ns[-1]:
        ii.append (len(ns)-1)

    re = []
    for i in xrange(len(dat)):
        re.append ([dat[i][j] for j in ii])
    return re

def get_var (fname):
    varis,ns = [],[]
    with open(fname) as f:
        for line in f:
            if 'Loaded MP state' in line:
                n = int(line.split('_')[-2])
            if 'up-to-two-site' in line:
                var = float(line.split()[-1])
                ns.append (n)
                varis.append (var)
    return ns, varis

def get_data (fname, mmin=64, var_file=''):
    its,ns,ens,enps,terrs,ms,msu2s,clocks,cputimes = getdata_full (fname)

    print 'n E E/N TruncErr m m(SU2)'
    for i,j,k,p,q,r in zip(ns,ens,enps,terrs,ms,msu2s): print i,j,k,p,q,r

    ns,ens,enps,terrs,ms,msu2s = takedata_eachm ((ns,ens,enps,terrs,ms,msu2s), ns, ms, mmin)
    print
    print 'n E E/N TruncErr m m(SU2)'
    for i,j,k,p,q,r in zip(ns,ens,enps,terrs,ms,msu2s): print i,j,k,p,q,r

    if var_file != '':
        ns_var, var = get_var (var_file)
        ind = ns_var.index(ns[0])
        ns_var = ns_var[ind:]
        var = var[ind:]

        print '\nn en_var'
        for i,j in zip(ns_var,var): print i,j

        terrs = var
        enps = enps[:len(var)]

    return terrs, enps

if __name__ == '__main__':
    fname = sys.argv[1]
    mmin = 64
    var_file = ''
    fitn = 0
    if '-minm' in sys.argv:
        mmin = int(sys.argv[sys.argv.index('-minm')+1])
    if '-var' in sys.argv:
        var_file = sys.argv[sys.argv.index('-var')+1]
    if '-fitn' in sys.argv:
        fitn = int(sys.argv[sys.argv.index('-fitn')+1])

    terrs, enps = get_data (fname, mmin, var_file)

    if fitn != 0:
        terrs = terrs[-fitn:]
        enps  = enps[-fitn:]
    f,ax = pl.subplots()
    ax.plot (terrs, enps, 'ok')
    fitx, fity, stddev = myfit (terrs, enps, werr=terrs, ax=ax, pltargs={'c':'k','marker':'None'})
    if var_file == '': xlabel = 'Truncation error'
    else: xlabel = 'Energy variance'
    pl.xlabel (xlabel,fontsize=18)
    pl.ylabel ('Energy per site',fontsize=18)

    print '\nfitted points:'
    print 'trunerr\ten_per_site'
    for te,en in zip(terrs,enps): print te,'\t',en
    print '\nenergy per site =',fity[-1],'+-',0.2*abs(fity[-1]-enps[-1]),'(stddev='+str(stddev)+')'

    pl.show()
