import os, sys
pylib = os.environ['SYTENDIRREAL']+'/pylib'
sys.path.append(pylib)
import pyten as p
import pyten_measure as mea
import subprocess

def get_print (command):
    return subprocess.check_output (command.split(), universal_newlines=True)

def get_pairing_terms (latt_file):
    sytendir = os.environ['SYTENDIRREAL']
    lat_info = get_print (sytendir+'/bin/syten-info '+latt_file)

    lines = lat_info.split('\n')
    hps = []
    for line in lines:
        if 'Hp' in line:
            hps.append (line.split()[0])
    return hps

def gen_pairing_mpos (hps, lat):
    indss = []
    for hp in hps:
        inds = list(map(int,hp.split('_')[1:]))
        inds = [i-1 for i in inds]
        indss.append (inds)
    #inds = [list(map(int,i.split('_')[1:])) for i in hps]

    mpos = [lat.get(i) for i in hps]
    return indss, mpos

def print_pairing_terms (hps, fname=''):
    if fname != '':
        f = open(fname,'w')

    for hp in hps:
        hp_str = hp+' { '+hp+' }'
        if fname == '':
            print (hp_str)
        else:
            print (hp_str, file=f)

    if fname != '':
        f.close()

if __name__ == '__main__':
    lat_file = sys.argv[1]
    psi_file = sys.argv[2]

    print ('Loading lattice',lat_file)
    lat = p.mp.Lattice (lat_file)
    print ('Loading MPS',psi_file)
    mps = p.mp.MPS()
    mps.setMaybeCache (True)
    mps.load (psi_file)

    hps = get_pairing_terms (lat_file)
    indss, mpos = gen_pairing_mpos (hps, lat)

    vals = mea.compute_expectations (indss, mpos, mps)

    out_file = psi_file+'.pair'
    with open(out_file,'w') as f:
        print ('x1 y1 x2 y2 delta', file=f)
        for inds,val in zip(indss,vals):
            print (*inds, val, file=f)
