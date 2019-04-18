import sys, os, glob
import pylab as pl
from discwt2 import getdata_full, takedata_eachm
from dmrg import read_para

def get_n_final (fname):
    si_dict = {}
    with open(fname) as f:
        for line in f: break
        for line in f:
            tmp = line.split()
            si = int(tmp[0])
            ni = float(tmp[1])
            si_dict[si] = ni
    sites,ns = si_dict.keys(), si_dict.values()
    sites,ns = map(list,zip(*sorted(zip(sites,ns)))) # sort
    return sites, ns

def get_n (fname):
    with open(fname) as f:
        ns = []
        for line in f: break
        for line in f:
            tmp = line.split()
            site,n = int(tmp[0]), float(tmp[1])
            N = site+1
            ns.append ([float('Nan') for i in xrange(N)])
            ns[-1][site] = n
            break
        for line in f:
            tmp = line.split()
            site,n = int(tmp[0]), float(tmp[1])
            if site >= len(ns[-1]):
                # extend ns[-1]
                N = site+1
                for i in xrange(N-len(ns[-1])):
                    ns[-1].append (float('Nan'))
            ns[-1][site] = n
            if site == 0 or site == len(ns[-1])-1:
                ns.append([float('Nan') for i in xrange(N)])
                ns[-1][site] = n
        return ns

def reshape_2d (dat,lx,ly):
    size = lx*ly
    re = []
    for i in xrange(0,size,ly):
        re.append (dat[i:i+lx])
    return zip(*re)

def plot_final (fname):
    si, ns = get_n_final (fname)
    hn = [1.-n for n in ns]
    hn = reshape_2d (hn,lx,ly)
    for h in hn:
        pl.plot (range(len(h)),h,marker='o')
    pl.show()

if __name__ == '__main__':
    if '-auto' in sys.argv:
        fname = glob.glob("*.e_n_1log")[0]
        fout = glob.glob("*.out")[0]
    else:
        fname = sys.argv[1]
        fout = sys.argv[2]
    mmin = 0
    if '-minm' in sys.argv:
        mmin = int(sys.argv[sys.argv.index('-minm')+1])

    its,ns,ens,enps,terrs,ms,msu2s,clocks,cputimes = getdata_full (fout)
    lx,ly = read_para (fout, ('lx','ly'), int, '=')

    dens = get_n (fname)
    dens = dens[:len(its)]

    its,ms,dens = takedata_eachm ((its,ms,dens), ns, ms, mmin=mmin)
    figfiles = ''
    for m,den in zip(ms,dens):
        pl.figure()
        hn = [1.-ni for ni in den]
        #print hn
        hn = reshape_2d (hn,lx,ly)
        for h in hn:
            pl.plot (range(len(h)),h,marker='o')
        pl.xlabel ('x',fontsize=18)
        pl.ylabel ('hole density',fontsize=18)
        pl.title ('m='+str(m))
        if '-pdf' in sys.argv:
            figfile = fname+'_m'+str(m)+'.pdf'
            pl.savefig (figfile)
            figfiles += ' '+figfile
        else:
            pl.show()

    if '-pdf' in sys.argv:
        outfile = fname+'.pdf'
        os.system ('gs -sDEVICE=pdfwrite -dEPSCrop -dNOPAUSE -dBATCH -dSAFER -sOutputFile='+outfile+figfiles)
        os.system ('rm '+figfiles)
