from readpara import read_para, read_block, read_block_terms

def addH (H, Hi):
    if Hi == '': return H
    elif H == '': return Hi
    else: return H + ' '+Hi + ' +'

def AddHs (H, Hs):
    for h in Hs:
        H = addH (H, h)
    return H

def HubH (U, tp=0., mu=0., t=1.):
    H = ''
    if U != 0.:
        H = addH (H, 'Hd '+str(U)+' *')
    if t != 0.:
        H = addH (H, 'Ht '+str(t)+' *')
    if tp != 0.:
        H = addH (H, 'Htp '+str(tp)+' *')
    if mu != 0.:
        H = addH (H, 'HN '+str(-mu)+' *')
    return H

def gen_H_tprime (tp,lx,ly,xpbc=0,ypbc=1):
    def in_system (x,y):
        if x > lx and xpbc: x -= lx
        if x < 1  and xpbc: x += lx
        if y > ly and ypbc: y -= ly
        if y < 1  and ypbc: y += ly
        isin = True
        if x > lx or x < 1: isin = False
        if y > ly or y < 1: isin = False
        return isin, x, y
    Hs = []
    for x1 in xrange(1,lx+1):
        for y1 in xrange(1,ly+1):
            i1 = xy_to_index (x1,y1,lx,ly)
            xy2 = [[x1+1,y1+1], [x1+1,y1-1]]
            for x2, y2 in xy2:
                isin, x2, y2 = in_system (x2,y2)
                if isin:
                    i2 = xy_to_index (x2,y2,lx,ly)
                    Hs.append (' c '+str(i1)+' @ c '+str(i2)+' @ _dot '+str(-tp)+' * + c '+str(i2)+' @ c '+str(i1)+' @ _dot '+str(-tp)+' *')
    return Hs

def gen_Ht_diag_lat (lx,ly,symm,ypbc=1,t=1.):
    bonds = []
    for yi in xrange(1,ly+1):
        for xi in xrange(1,lx):
            bonds.append ([xi,yi,xi+1,yi])
    for xi in xrange(1,lx,2):
        for yi in xrange(2,ly+1):
            bonds.append ([xi,yi,xi+1,yi-1])
        if ypbc:
            bonds.append ([xi,1,xi+1,ly])
    for xi in xrange(2,lx,2):
        for yi in xrange(1,ly):
            bonds.append ([xi,yi,xi+1,yi+1])
        if ypbc:
            bonds.append ([xi,ly,xi+1,1])

    Hs = []
    for x1,y1,x2,y2 in bonds:
        i1 = xy_to_index (x1,y1,lx,ly)
        i2 = xy_to_index (x2,y2,lx,ly)
        if symm == 'su2':
            Hs.append('c '+str(i1)+' @ c '+str(i2)+' @ _dot '+str(-t)+' *')
            Hs.append('c '+str(i2)+' @ c '+str(i1)+' @ _dot '+str(-t)+' *')
        elif symm == 'u1':
            Hs.append('chu '+str(i1)+' @ cu '+str(i2)+' @ * '+str(-t)+' *')
            Hs.append('chu '+str(i2)+' @ cu '+str(i1)+' @ * '+str(-t)+' *')
            Hs.append('chd '+str(i1)+' @ cd '+str(i2)+' @ * '+str(-t)+' *')
            Hs.append('chd '+str(i2)+' @ cd '+str(i1)+' @ * '+str(-t)+' *')
        else:
            print 'Unknown symmetry:',symm
            raise KeyError
    return Hs

def xy_to_index (x,y,lx,ly):
# x,y is 1-indexed and index is 0-indexed
    return (y-1)+(x-1)*ly

def gen_H_pairing (x1y1x2y2D,lx,ly):
    Hs = []
    for x1,y1,x2,y2,D in x1y1x2y2D:
        if D != 0.:
            Hs.append ('Hp_'+str(x1)+'_'+str(y1)+'_'+str(x2)+'_'+str(y2)+' '+str(D)+' *')
    return Hs

def gen_H_localmuh (xymuh,lx,ly):
    Hs = []
    for x,y,mu,h in xymuh:
        ind = xy_to_index (x,y,lx,ly)
        if mu != 0.:
            Hs.append ('n '+str(ind)+' @ '+str(-mu)+' *')
        if h != 0.:
            Hs.append ('sz '+str(ind)+' @ '+str(h)+' *')
    return Hs

def gen_H_globalmu (mu,lx,ly):
    Hs = []
    for ind in xrange(lx*ly):
        Hs.append ('n '+str(ind)+' @ '+str(-mu)+' *')
    return Hs

def read_muh_each (fname):
    xymu = []
    f = open(fname)
    for line in f:
        if line.strip() == 'localmuh':
            for line in f:
                if 'x' in line and 'y' in line and 'mu' in line and 'h' in line: break
            for line in f:
                if '}' in line: break
                else:
                    tmp = line.split()
                    x, y = map(int,tmp[:2])
                    mu,h = map(float,tmp[2:4])
                    xymu.append ([x,y,mu,h])
    return xymu

def vertical_stripe_muh (lx,ly,xs,mu,h):
    xymuh = []
    idomain = 0
    hsign = 1.
    for x in xrange(1,lx+1):
        for y in xrange(1,ly+1):
            if x in xs:
                mui = mu
                hi = 0.
            else:
                if idomain < len(xs) and x > xs[idomain]:
                    hsign *= -1.
                    idomain += 1
                mui = 0.
                hi = hsign * h * (-1)**(x % 2 == y % 2)
            xymuh.append ([x,y,mui,hi])
    return xymuh

def linear_mu (lx,ly,mu1,mu2):
    dmu = float(mu2 - mu1)/float(lx-1)
    xymuh = []
    for x in xrange(1,lx+1):
        for y in xrange(1,ly+1):
            mui = mu1 + (x-1)*dmu
            xymuh.append ([x,y,mui,0.])
    return xymuh

def localmuh (fname):
    lx,ly = read_para (fname, ('lx','ly'), int, '=')

    para = read_block (fname, 'localmuh')
    if para == None:
        return ''
    elif 'type' in para:
        if para['type'] == 'vertical_stripes':
            xymuh = vertical_stripe_muh (lx,ly,para['stripe_x'],para['stripe_mu'],para['stripe_h'])
        elif para['type'] == 'global_mu':
            return gen_H_globalmu (para['mu'],lx,ly)
        elif para['type'] == 'linear_mu':
            xymuh = linear_mu (lx,ly,para['mu1'],para['mu2'])
        else:
            print 'Unknow type in localmuh'
            raise Exception
    else:
        xymuh = read_muh_each (fname)

    return gen_H_localmuh (xymuh,lx,ly)

def global_dwave_pairing_terms (lx,ly,delta,xpbc=False,ypbc=True):
    dels = []
    for y in xrange(1,ly+1):
        for x in xrange(1,lx+1):
            # horizontal bonds
            if x != lx:
                dels.append ([x,y,x+1,y,delta])
            # vertical bonds
            if y == ly:
                if ypbc:
                    y2 = 1
                    dels.append ([x,y,x,y2,-delta])
            else:
                y2 = y+1
                dels.append ([x,y,x,y2,-delta])
    return dels

def pairing_terms (fname):

    lx,ly = read_para (fname, ('lx','ly'), int, '=')
    para = read_block (fname, 'pairing_potential')
    if para == None: return ''

    symm = read_para (fname, 'symm', str, '=')
    if symm != 'su2gc':
        print 'pairing potential is available for only grand canonical simulations'
        raise Exception

    if 'type' in para:
        if para['type'] == 'dwave':
            x1y1x2y2D = global_dwave_pairing_terms (lx,ly,para['delta'])
        else:
            return ''
    else:
        x1y1x2y2D = read_block_terms (fname, 'pairing_potential', ('x1','y1','x2','y2','D'))

    return gen_H_pairing (x1y1x2y2D,lx,ly)
