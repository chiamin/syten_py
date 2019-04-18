import sys
#sys.path.append ('/home/chiamin/mypy/syten')
from paircorr import x_pair_corr_sites, read_pair_corr_dat, pair_corr_terms
import pylab as pl
from matplotlib import rc

def itoxy (i,lx,ly):
    x = i/ly+1
    y = i%ly+1
    return x, y

def get_pair_corr (x,y,lx,ly,fname):
    ppairs,xyppair = x_pair_corr_sites (x,y,lx,ly)
    cc = read_pair_corr_dat (fname)
    pcorr = []
    for i,j,ip,jp in ppairs:
        obs,terms,coefs = pair_corr_terms (i,j,ip,jp)
        val = 0.
        for o,coef in zip(obs,coefs):
            val += coef*cc[o]

            #if i == ip or i == jp or j == ip or j == jp:
            #    print i,j,ip,jp,':',coef,o,cc[o]

        pcorr.append (val)
    return ppairs,xyppair,pcorr

def get_pair_corr_2 (fname, lx, ly, x, y):
    ppairs,xyppair,pcorr = get_pair_corr (x,y,lx,ly,fname)
    hor_corr, ver_corr, hor_x, ver_x = [],[],[],[]
    for i in xrange(len(ppairs)):
        x1,y1,x2,y2,xp1,yp1,xp2,yp2 = xyppair[i]
        corr = pcorr[i]
        if xp1 != xp2:
            hor_x.append (xp1)
            hor_corr.append (corr)
        else:
            ver_x.append (xp1)
            ver_corr.append (corr)
    return hor_x, hor_corr, ver_x, ver_corr


def plot_pair_corr (ax, fname, lx, ly, x, y, typ='', logxy='', **kwargs):
    ppairs,xyppair,pcorr = get_pair_corr (x,y,lx,ly,fname)
    hor_corr, ver_corr, hor_x, ver_x = [],[],[],[]
    for i in xrange(len(ppairs)):
        x1,y1,x2,y2,xp1,yp1,xp2,yp2 = xyppair[i]
        corr = pcorr[i]
        if xp1 != xp2:
            hor_x.append (xp1)
            hor_corr.append (corr)
        else:
            ver_x.append (xp1)
            ver_corr.append (corr)

    if logxy == '-logx' or logxy == '-logy' or logxy == '-logxy':
        ver_x_pos, ver_corr_pos = [],[]
        for xi, corr in zip(ver_x, ver_corr):
            if xi > x:
                ver_x_pos.append (xi-x)
                ver_corr_pos.append (corr)
        hor_x_pos, hor_corr_pos = [],[]
        for xi, corr in zip(hor_x, hor_corr):
            if xi > x:
                hor_x_pos.append (xi-x)
                hor_corr_pos.append (-corr)
        ver_x,ver_corr,hor_x,hor_corr = ver_x_pos,ver_corr_pos,hor_x_pos,hor_corr_pos

    if logxy == '-logx' or logxy == '-logxy':
        ax.set_xscale ('log')
    if logxy == '-logy' or logxy == '-logxy':
        ax.set_yscale ('log')

    autokw = (kwargs == {})
    if typ != 'hor':
        if autokw:
            kwargs = {'label':'vertical','marker':'o','ls':'None','ms':5}
        ax.plot (ver_x,ver_corr,**kwargs)
    if typ != 'ver':
        if autokw:
            kwargs = {'label':'horizontal','marker':'x','ls':'None','ms':6,'mew':1.5}
        ax.plot (hor_x,hor_corr,**kwargs)
    return ppairs,xyppair,pcorr


if __name__ == '__main__':
    rc('font', **{'family': 'DejaVu Sans', 'serif': ['Computer Modern']})
    rc('text', usetex=True)

    dmrgfile = sys.argv[1]
    pairfiles = [i for i in sys.argv[2:] if '-' not in i]
    with open(dmrgfile) as f:
        for line in f:
            if 'name' in line:
                name = line.split()[-1]
            elif 'lx' in line:
                lx = int(line.split()[-1])
            elif 'ly' in line:
                ly = int(line.split()[-1])
            elif '{' in line: break

    x,y = lx/2,1
    x = 5

    logxy = ''
    if '-logx' in sys.argv or '-logy' in sys.argv or '-logxy' in sys.argv:
        if '-logx' in sys.argv: logxy = '-logx'
        elif '-logy' in sys.argv: logxy = '-logy'
        elif '-logxy' in sys.argv: logxy = '-logxy'

    f, ax = pl.subplots()
    for pairfile in pairfiles:
        plot_pair_corr (ax, pairfile, lx, ly, x, y, logxy=logxy)
    pl.xlabel ('$x$',fontsize=16)
    pl.ylabel ("$\\langle \Delta^\dagger_{ij} \Delta_{i'j'} \\rangle$",fontsize=16)
    pl.legend ()
    pl.show()

    if '-pdf' in sys.argv:
        pl.savefig (fname+'_pcorr.pdf')

    if '-save' in sys.argv:
        datname = fname+'_pcorr.dat'
        with open(datname,'w') as f:
            f.write('pair-pair correlation related to x,y='+str(x)+','+str(y)+'\n')
            f.write('x1 y1 x2 y2 ppcorr\n')
            for i in xrange(len(ppairs)):
                x1,y1,x2,y2,xp1,yp1,xp2,yp2 = xyppair[i]
                corr = pcorr[i]
                f.write (str(xp1)+' '+str(yp1)+' '+str(xp2)+' '+str(yp2)+' '+str(corr)+'\n')
