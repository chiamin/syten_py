import os, sys, glob
import pylab as pl
from meahsz import get_lxy
from environ import syten_envi

def plot_hsz (lx,ly,fname):
    def toxy (i,lx,ly):
        return i/ly+1, i%ly+1

    f = open (fname)
    for line in f:
        if 'site n' in line: break
    h_dict, sz_dict = dict(), dict()
    for line in f:
        tmp = line.split()
        i,h = int(tmp[0]), 1-float(tmp[1])
        x,y = toxy (i,lx,ly)

        h_dict[x,y] = h
        if len(tmp) == 3:
            sz = float(tmp[2])
            sz_dict[x,y] = sz

    xs = range(1,lx+1)
    for y in xrange(1,ly+1):
        hx = []
        for x in xs:
            hx.append (h_dict[x,y])
        pl.plot (xs, hx, 'o-')
    pl.xlabel('x',fontsize=18)
    pl.ylabel('hole density',fontsize=18)

if __name__ == '__main__':
    syten_envi (sys.argv)
    sytendir = os.environ['SYTENDIR']

    wdir = os.getcwd()
    if '-auto' in sys.argv:
        lat = glob.glob("*.lat")[0]
        hszs = glob.glob("*.hsz")
    else:
        lat = sys.argv[1]
        hszs = sys.argv[2:]
    hszs.sort()

    lx,ly = get_lxy (sytendir, lat)
    figfiles = ''
    suf = 1
    for fname in hszs:
        print fname
        pl.figure()
        plot_hsz (lx,ly,fname)
        if '-pdf' in sys.argv:
            print fname
            figfile = fname+str(suf)+'.pdf'
            pl.savefig (figfile)
            figfiles += ' '+figfile
        else:
            pl.show()
        suf += 1

    outfile = hszs[0].split('_T')[0]+'.pdf'
    if '-pdf' in sys.argv:
        outfile = fname+'.pdf'
        os.system ('gs -sDEVICE=pdfwrite -dEPSCrop -dNOPAUSE -dBATCH -dSAFER -sOutputFile='+outfile+figfiles)
        os.system ('rm '+figfiles)
