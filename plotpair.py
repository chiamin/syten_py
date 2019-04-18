import sys
import pylab as pl

if __name__ == '__main__':
    fname = sys.argv[1]
    pairs = dict()
    with open(fname) as f:
        for line in f: break
        for line in f:
            tmp = line.split()
            x1,y1,x2,y2 = map(int,tmp[:4])
            pair = float(tmp[4])
            pairs[x1,y1,x2,y2] = pair

    lx = 64
    y = 2
    xs = range(1,lx+1)

    pv,ph = [],[]
    for x in xs:
        pv.append (pairs[x,y,x,y+1]) # vertical
        if x != lx:
            ph.append (pairs[x,y,x+1,y]) # horizontal

    pl.plot (xs,pv,'ok',label='ver')
    pl.plot (xs[:-1],ph,'or',label='hor')
    pl.legend (loc='best')
    pl.show()
