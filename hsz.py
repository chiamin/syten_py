import os, sys
from subprocess import call, check_output
import pylab as pl
from environ import syten_envi

def make_tmp (fname,N,symm='su2'):
    '''
    if os.path.isfile (fname):
        f = open (fname)
        lines = f.readlines()
        f.close()
        if len(lines) == N+1: return
    '''
    if symm == 'su2': s_op = 's'
    elif symm == 'u1': s_op = 'sz'

    f = open (fname, 'w')
    f.write ('site n '+s_op+'\n')
    for i in xrange(N):
        f.write (str(i)+' { n '+str(i)+' @ } { '+s_op+' '+str(i)+' @ }\n')
    f.close()

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

def plot_hsz (lx,ly,fname):
    def toxy (i,lx,ly):
        return i/ly+1, i%ly+1

    f = open (fname)
    for line in f:
        if 'site' in line and 'n' in line and 'sz' in line:
            break
    h_dict, sz_dict = dict(), dict()
    for line in f:
        tmp = line.split()
        if len(tmp) != 3: break
        i,h,sz = int(tmp[0]),1-float(tmp[1]),float(tmp[2])

        x,y = toxy (i,lx,ly)
        h_dict[x,y] = h
        sz_dict[x,y] = sz

    xs = range(1,lx+1)
    for y in xrange(1,ly+1):
        hx = []
        for x in xs:
            hx.append (h_dict[x,y])
        pl.plot (xs, hx, 'o-')
    pl.xlabel('x',fontsize=18)
    pl.ylabel('hole density',fontsize=18)

def do_hsz (sytendir, lat, psi, out='',symm='su2',cpus_dense=1,cpus_tensor=1,cpus_super=1,writeM=1048576,overwrite=False):
    tmp = 'mea.temp'
    if os.path.isfile (out) and overwrite: os.system ('rm '+out)
    commands = []
    if not os.path.isfile (out):
        N = get_N (sytendir, lat)
        make_tmp (tmp,N,symm)

        flag =  ' --cache --cache-threshold '+str(writeM)+' '
        flag += ' --threads-dense '+str(cpus_dense)+' '
        flag += ' --threads-tensor '+str(cpus_tensor)+' '
        flag += ' --threads-super '+str(cpus_super)+' '
        to_file = ''
        if out != '': to_file = ' 1>>'+out+' 2>&1'
        command = sytendir+'/bin/syten-expectation '+flag+' --template-file '+tmp+' -l '+lat+' '+psi+' -r'+to_file

        commands += ['echo '+command]
        commands += [command]
    return commands

if __name__ == '__main__':
    syten_envi (sys.argv)
    sytendir = os.environ['SYTENDIR']

    lat = sys.argv[1]
    psi_files = ''
    plot = False
    for f in sys.argv[2:]: psi_files += ' '+f+' '
    psi_files = check_output('ls '+psi_files, shell=True).split()

    if '-plt' in sys.argv: plot = True

    for psi in psi_files:
        out = ''
        if plot: out = psi.replace('.hsz','')+'.hsz'
        commands = do_hsz (sytendir, lat, psi, out, symm='u1')
        for command in commands:
            os.system (command)

        if plot:
            lx,ly = get_lxy (sytendir, lat)
            plot_hsz (lx,ly,out)
            pl.title (psi)
            pl.show()
