import os, sys, glob
from subprocess import call, check_output
from environ import syten_envi

def make_hsz_tmp (fname,N,symm='su2'):
    with open (fname, 'w') as f:
        if symm == 'su2':
            f.write ('site n\n')
            for i in xrange(N):
                f.write (str(i)+' { n '+str(i)+' @ }\n')
        elif symm == 'u1':
            f.write ('site n sz\n')
            for i in xrange(N):
                f.write (str(i)+' { n '+str(i)+' @ } { sz '+str(i)+' @ }\n')

def get_N (sytendir, lat):
    command = sytendir+'/bin/syten-info '+lat
    lines = check_output(command, shell=True)
    lines = lines.rstrip().split('\n')
    for line in lines:
        if 'Number of sites' in line:
            return int(line.split()[-1])

def get_lxy (sytendir, lat):
    command = sytendir+'/bin/syten-info '+lat
    lines = check_output(command, shell=True)
    lines = lines.rstrip().split('\n')
    for line in lines:
        if 'lattice' in line and 'dimension' in line:
            tmp = line.split()
            ind = tmp.index('dimension')
            tmp = tmp[ind+1].split('\xc3\x97')
            return int(tmp[0]),int(tmp[1])

def get_symm (sytendir, lat):
    command = sytendir+'/bin/syten-info '+lat
    lines = check_output(command, shell=True)
    lines = lines.rstrip().split('\n')
    for line in lines:
        if 'symmetric' in line and 'lattice' in line:
            tmp = line.split()
            if 'U(1)\xc3\x97U(1)' in tmp:
                return 'u1'
            elif 'U(1)_N' in tmp and 'SU(2)_S' in tmp:
                return 'su2'
            else:
                print 'Unrecognized symmetry'
                raise KeyError

def mea_hsz_commands (sytendir, lat, psi, tmp='meahsz.temp',cpus_dense=1,cpus_tensor=1,cpus_super=1,writeM=1048576,pprint=False):
    commands = []

    N = get_N (sytendir, lat)
    symm = get_symm (sytendir, lat)
    make_hsz_tmp (tmp,N,symm)

    out_file = psi+'.hsz'
    flag =  ' --cache --cache-threshold '+str(writeM)+' '
    flag += ' --threads-dense '+str(cpus_dense)+' '
    flag += ' --threads-tensor '+str(cpus_tensor)+' '
    flag += ' --threads-super '+str(cpus_super)+' '
    command = sytendir+'/bin/syten-expectation '+flag+' --template-file '+tmp+' -l '+lat+' -a '+psi+' -r >'+out_file
    commands += ['echo '+command]
    commands += [command]

    if pprint:
        for i in commands: print i
    return commands

if __name__ == '__main__':
    syten_envi (sys.argv)
    sytendir = os.environ['SYTENDIR']

    wdir = os.getcwd()
    if '-auto' in sys.argv:
        lat = glob.glob("*.lat")[0]
        psi_files = glob.glob("*.state")
    else:
        lat = sys.argv[1]
        psi_files = sys.argv[2:]
    for i in xrange(len(psi_files)):
        if '/' not in psi_files[i]:
            psi_files[i] = wdir+'/'+psi_files[i]


    print '# lattice:',lat
    print '# psi:',psi_files

    for psi in psi_files:
        commands = mea_hsz_commands (sytendir, lat, psi, pprint=True)

