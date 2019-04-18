import os, sys, glob
from subprocess import check_output
from hsz import do_hsz
from envari import do_en_vari
from dmrg import read_H
from subprocess import call, check_output, STDOUT, CalledProcessError
from environ import syten_envi
from readpara import read_para, read_lat

def hsz_fname (psi_fname): return psi_fname.replace('.hsz','')+'.hsz'
def mea_fname (job_name): return job_name.replace('.mea','')+'.mea'

def readpara (fname):
    f = open (fname)
    for line in f:
        if   'name' in line: name = line.split()[-1]
        elif 'workdir' in line: workdir = line.split()[-1]
        elif 'outdir' in line: outdir = line.split()[-1]
        elif 'cpus_dense' in line: cpus_dense = int(line.split()[-1])
        elif 'cpus_tensor' in line: cpus_tensor = int(line.split()[-1])
        elif 'cpus_super' in line: cpus_super = int(line.split()[-1])
        elif 'writeM' in line: writeM = int(line.split()[-1])
        elif 'symm' in line: symm = line.split()[-1]
    return name,workdir,outdir,cpus_dense,cpus_tensor,cpus_super,writeM,symm

def read_arg (fname, key, arg):
    f = open (fname)
    for line in f:
        if key in line:
            tmp = line.split()
            ind = tmp.index(arg)
            re = tmp[ind+1]
            return re

def make_tmp_pairing (fname,lx,ly):
    f = open (fname, 'w')
    f.write ('x1 y1 x2 y2 pairing\n')
    for x in xrange(1,lx+1):
        for y in xrange(1,ly+1):
            if ly != 1:
                x2, y2 = x, y%ly+1
                f.write (str(x)+' '+str(y)+' '+str(x2)+' '+str(y2)+' { Hp_'+str(x)+'_'+str(y)+'_'+str(x2)+'_'+str(y2)+' }\n')
            if x != lx:
                x2, y2 = x+1, y
                f.write (str(x)+' '+str(y)+' '+str(x2)+' '+str(y2)+' { Hp_'+str(x)+'_'+str(y)+'_'+str(x2)+'_'+str(y2)+' }\n')
    f.close()

if __name__ == '__main__':
    syten_envi (sys.argv)
    sytendir = os.environ['SYTENDIR']

    outfile = sys.argv[1]
    jname,wdir,odir,symm = read_para (outfile, ('name','workdir','outdir','symm'), str, '=')
    lx,ly,cpus_dense,cpus_tensor,cpus_super,writeM = read_para (outfile, ('lx','ly','cpus_dense','cpus_tensor','cpus_super','writeM'), int, '=')
    H = read_H (outfile)
    if '-odir' in sys.argv:
        odir = sys.argv[sys.argv.index('-odir')+1]
    if '-wdir' in sys.argv:
        wdir = sys.argv[sys.argv.index('-wdir')+1]
    if '-cpus_dense' in sys.argv:
        cpus_dense = sys.argv[sys.argv.index('-cpus_dense')+1]
    if '-cpus_tensor' in sys.argv:
        cpus_tensor = sys.argv[sys.argv.index('-cpus_tensor')+1]
    if '-cpus_super' in sys.argv:
        cpus_super = sys.argv[sys.argv.index('-cpus_super')+1]

    wdir = os.getcwd()
    lat = glob.glob("*.lat")[0]

    #lat = read_lat (outfile)
    lat = wdir+'/'+lat
    psi_prefix = read_arg (outfile,'syten-dmrg','-o').split('/')[-1]
    psi_files = (check_output('ls '+wdir+'/'+psi_prefix+'*.state', shell=True)).split()
    psi_files = [psi.split('/')[-1] for psi in psi_files]
    #print 'lattice:',lat
    #print 'psi:',psi_files

    swpn = [int(psi.split('_')[-2]) for psi in psi_files]
    psi_files = [x for _,x in sorted(zip(swpn,psi_files))]

    mea_out = odir+'/'+mea_fname (jname)
    if os.path.isfile (mea_out):
        f = open (mea_out)
        oldfile = f.read()
    else:
        oldfile = ''

    flag =  ' --cache --cache-threshold '+str(writeM)+' '
    flag += ' --threads-dense '+str(cpus_dense)+' '
    flag += ' --threads-tensor '+str(cpus_tensor)+' '
    flag += ' --threads-super '+str(cpus_super)+' '

    commands = []
    for psi in psi_files:
        # hsz
        psi_full = wdir+'/'+psi
        endline = 'Finished measuring '+psi_full
        #hsz_out  = odir+'/'+hsz_fname (psi)
        #if not os.path.isfile (hsz_out):
        #    print psi,': measure hsz'
        #    do_hsz (sytendir, lat, psi_full, hsz_out, cpus_dense, cpus_tensor, cpus_super, writeM)

        # energy variance
        if not os.path.isfile (mea_out) or psi not in oldfile:
            commands += ['echo "measure en variance: '+psi+'"']
            commands += do_en_vari (sytendir, lat, psi_full, H, cpus_dense, cpus_tensor, cpus_super, writeM)

        # pairing
        #if symm == 'su2gc':
        #    tmp = 'pairing.tmp'
        #    make_tmp_pairing (tmp,lx,ly)
        #    commands += [sytendir+'/bin/syten-expectation '+flag+' --template-file '+tmp+' -l '+lat+' -a '+psi_full+' -r']

        #commands += ['echo "'+end_line+'"']

        commands += ['rm *.cache']

    for command in commands:
        print command
        print
        continue
        with open(mea_out,'a') as f:
            try:
                tmp = check_output (command,shell=True,stderr=STDOUT)
                f.write (tmp)
                f.write ('\n')
                #print tmp
            except CalledProcessError as e:
                print e.output
                raise Exception
