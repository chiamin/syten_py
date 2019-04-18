import sys,glob,os
from environ import syten_envi

# Terms to compute D+_ij D_ij, where D_ij = (1/sqrt2) (c_i_up c_j_dn - c_i_dn c_j_up)
def pair_corr_terms (i,j,ip,jp):
    i,j,ip,jp = str(i),str(j),str(ip),str(jp)
    terms,obs,coefs = [],[],[]
    obs.append ('(c_i^+.c_j)(c_k^+.c_l):i,j,k,l='+i+','+ip+','+j+','+jp)
    terms.append ('c '+i+' @ c '+ip+' @ _dot c '+j+' @ c '+jp+' @ _dot * ')
    coefs.append (.5)
    obs.append ('(c_i^+.c_j)(c_k^+.c_l):i,j,k,l='+i+','+jp+','+j+','+ip)
    terms.append ('c '+i+' @ c '+jp+' @ _dot c '+j+' @ c '+ip+' @ _dot * ')
    coefs.append (.5)
    if ip == j:
        obs.append ('c_i^+.c_j:i,j='+i+','+jp)
        terms.append ('c '+i+' @ c '+jp+' @ _dot ')
        coefs.append (-.5)
    if jp == j:
        obs.append ('c_i^+.c_j:i,j='+i+','+ip)
        terms.append ('c '+i+' @ c '+ip+' @ _dot ')
        coefs.append (-.5)
    return obs,terms,coefs

def gen_mea_file (ppair,fname):
    with open(fname,'w') as f:
        for i,j,ip,jp in ppair:
            obs,terms,coefs = pair_corr_terms (i,j,ip,jp)
            for o,term in zip(obs,terms):
                #f.write (o+' '+'{ '+term+' }\n')
                print >>f, o+' '+'{ '+term+' }'

def xytoi (x,y,lx,ly):
    x -= 1
    y -= 1
    return x*ly + y

def x_pair_corr_sites (x,y,lx,ly):
    if y+1 > ly:
        print 'y+1 > ly, y=',y
        raise ValueError
    ppair,xyppair = [],[]
    i = xytoi (x,y,lx,ly)
    j = xytoi (x,y+1,lx,ly)
    for xp in xrange(1,lx+1):
        ip = xytoi (xp,y,lx,ly)
        jp = xytoi (xp,y+1,lx,ly)
        ppair.append ([i,j,ip,jp])
        xyppair.append ([x,y,x,y+1,xp,y,xp,y+1])
        if xp < lx-1:
            jp = xytoi (xp+1,y,lx,ly)
            ppair.append ([i,j,ip,jp])
            xyppair.append ([x,y,x,y+1,xp,y,xp+1,y])
    return ppair,xyppair

def all_pair_corr_sites (x,y,lx,ly):
    ppair,xyppair = [],[]
    i = xytoi (x,y,lx,ly)
    j = xytoi (x,y+1,lx,ly)
    for yp in xrange(1,ly+1):
        for xp in xrange(1,lx+1):
            yup = yp+1
            if yup > ly: yup -= ly
 
            ip = xytoi (xp,yp,lx,ly)
            jp = xytoi (xp,yup,lx,ly)
            ppair.append ([i,j,ip,jp])
            xyppair.append ([x,y,x,y+1,xp,yp,xp,yup])
            if xp < lx:
                jp = xytoi (xp+1,yp,lx,ly)
                ppair.append ([i,j,ip,jp])
                xyppair.append ([x,y,x,y+1,xp,yp,xp+1,yp])
    return ppair,xyppair

def gen_x_pair_corr (y,lx,ly,fname):
    gen_mea_file (ppair,fname)

def read_pair_corr_dat (fname):
    dat = dict()
    with open(fname) as f:
        for line in f:
            obs,val = line.split()
            dat[obs] = float(val)
    return dat

def get_pair_corr (x,y,lx,ly,fname):
    ppairs,xyppair = x_pair_corr_sites (x,y,lx,ly)
    cc = read_pair_corr_dat (fname)
    pcorr = []
    for i,j,ip,jp in ppairs:
        obs,terms,coefs = pair_corr_terms (i,j,ip,jp)
        val = 0.
        for o,coef in zip(obs,coefs):
            val += coef*cc[o]
        pcorr.append (val)
    return ppairs,pcorr

if __name__ == '__main__':
    if '-auto' in sys.argv:
        outname = glob.glob("h*.out")[0]
    else:
        outname = sys.argv[1]
    with open(outname) as f:
        for line in f:
            if 'name' in line:
                name = line.split()[-1]
            elif 'lx' in line:
                lx = int(line.split()[-1])
            elif 'ly' in line:
                ly = int(line.split()[-1])
            elif '{' in line: break
    meatmp = name+'.paircor.mea'

    #x,y = lx/2,1
    x,y = 5,1

    ppairs,xyppair = x_pair_corr_sites (x,y,lx,ly)
    #ppairs,xyppair = all_pair_corr_sites (x,y,lx,ly) 
    gen_mea_file (ppairs,meatmp)
    exit()

    syten_envi (sys.argv)
    wdir = os.getcwd()
    latt = glob.glob("*.lat")[0]
    psifiles = glob.glob("*.state")
    cpus  = 32
    writeM = 8388608
    EXE = os.environ['SYTENDIR']+'/bin/syten-expectation'
    pairmea = glob.glob("*.paircor.mea")[0]

    for psifile in psifiles:
        print EXE+" -l "+wdir+"/"+latt+" --template-file "+wdir+"/"+pairmea+" -a "+wdir+"/"+psifile+" --threads-tensor "+str(cpus)+" --cache --cache-threshold "+str(writeM)+" >> "+wdir+"/"+psifile+".paircorr"
