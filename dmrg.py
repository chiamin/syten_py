from subprocess import call
import os, sys, glob
from hamilt import HubH, localmuh, pairing_terms, AddHs, gen_Ht_diag_lat, addH
import genstate
from readpara import read_para
from genlatt import genlatt
from environ import syten_envi
from paircorr import *

def sys_command (command, echo=True):
    if echo: call(('echo '+command).split())
    os.system (command)

def echo_command (command):
    return ['echo '+command, command]

def readparas (fname):
    name,symm,workdir,outdir = read_para (fname, ('name','symm','workdir','outdir'), str, '=')
    lx,ly,cpus_dense,cpus_tensor,cpus_super,writeM = read_para (fname, ('lx','ly','cpus_dense','cpus_tensor','cpus_super','writeM'), int, '=')
    Stot = read_para (fname, 'Stot', float, '=')

    f = open (fname)
    for line in f:
        if 'Npar' in line and '=' in line:
            if '(' in line:
                tmp = line.split()[-1]
                tmp = tmp.lstrip('(')
                tmp = tmp.rstrip(')')
                tmp = tmp.split('/')
                nume,deno = map(int,tmp)
                Npar = lx*ly*nume/deno
            else:
                Npar = int(line.split()[-1])

        if line.strip() == 'sweeps':
            sweeps = []
            for line in f:
                if 'm' in line: break
            for line in f:
                if '}' in line: break
                else:
                    tmp = line.split()
                    m, Nswp, maxIter = map(int,tmp[:3])
                    cutoff = float(tmp[3])
                    subspace = int(tmp[4])
                    if len(tmp) > 5:
                        dmrgtype = tmp[5]
                        if dmrgtype == '2': dmrgtype = '2DMRG'
                        elif dmrgtype == '1': dmrgtype = 'DMRG3S'
                        else: dmrgtype = ''
                    else:
                        dmrgtype = read_para (fname, 'dmrgtype', str, '=')
                    sweeps.append ([m,Nswp,maxIter,cutoff,subspace,dmrgtype])

    return name,lx,ly,Npar,Stot,symm,sweeps,workdir,outdir,cpus_dense,cpus_tensor,cpus_super,writeM

def read_H (fname):
    spec = read_para (fname, 'special', str, '=', default='')
    symm = read_para (fname, 'symm', str, '=')
    lx,ly = read_para (fname, ('lx','ly'), int, '=')
    U  = read_para (fname, 'U', float, '=')
    t, mu, tp = read_para (fname, ('t','mu','tp'), float, '=', default=(1.,0.,0.))
    if spec == '':
        H = HubH (U, tp=tp, mu=mu, t=t)
    elif spec == 'diag_latt':
        H = ''
        H = AddHs (H, gen_Ht_diag_lat (lx,ly,symm,ypbc=1,t=t))
        H = addH (H, HubH (U, t=0., mu=mu))
    else:
        print 'Unkown special setting:',spec
        raise KeyError
    H = AddHs (H, localmuh (fname))
    H = AddHs (H, pairing_terms (fname))
    return H

def runDMRG (sytendir, latt, H, initState, sweeps, name, cpus_dense=1,cpus_tensor=1,cpus_super=1,writeM=1048576,do_variance=True):
    flags  = ' --threads-dense '+str(cpus_dense)
    flags += ' --threads-tensor '+str(cpus_tensor)
    flags += ' --threads-super '+str(cpus_super)
    flags += ' --cache --cache-threshold '+str(writeM)
    flags += ' --local-expectations '+latt+':n '
    bash = 'SYTEN_MEMORY_SAMPLER=memsampley SYTEN_MEMORY_SAMPLER_SAMPLES=6000 SYTEN_MEMORY_SAMPLER_INTERVAL=10 '
    command = bash+' '+sytendir+'/bin/syten-dmrg '+flags+' -l '+latt+':"'+H+'" -i '+initState+' -s "'
    for m,Nswp,maxIter,cutoff,subspace,dmrgtype in sweeps:
        command += '(v '+dmrgtype+' m '+str(m)+' x '+str(2*Nswp)+' e { x '+str(maxIter)+' } eb '+str(subspace)+' t '+str(cutoff)+' convMinEnergyDiff -1) '
        if do_variance:
            command += '(v 2svar) '
    command += '" -o '+name

    commands  = ['echo','echo',"echo '* Run DMRG'"]
    commands += echo_command (command)
    commands += ["echo '* Done DMRG'"]
    return commands

def readState (fname):
    with open(fname) as f:
        for line in f:
            if line.strip() == 'readState':
                for line in f:
                    if '}' in line:
                        return latt, state
                    rdir,latt,state = read_para (fname, ('dir','lattice','state'), str, '=')
                    latt = rdir+'/'+latt
                    state = rdir+'/'+state
                    if not os.path.isfile (latt):
                        print 'Lattice file',latt,'does not exist'
                        raise Exception 
                    if not os.path.isfile (state):
                        print 'State file',state,'does not exist'
                        raise Exception                    
    raise KeyError

def dmrg_commands (fname, sytendir):
    name,lx,ly,Npar,Stot,symm,sweeps,workdir,outdir,cpus_dense,cpus_tensor,cpus_super,writeM = readparas (fname)
    name = workdir+'/'+name+'_'+str(lx)+'x'+str(ly)+'_'+symm

    commands = ['cat '+fname]

    try:
        # Check if read initial state from file
        latt,initstate = readState (fname)
        commands += ['echo Read lattice from '+latt]
        commands += ['echo Read initial state from '+initstate]
        lattwdir = workdir+'/'+os.path.basename(latt)
        if not os.path.isfile (lattwdir):
            commands += ['cp '+latt+' '+lattwdir]
    except KeyError:
        # Generate lattice
        latt,command = genlatt (sytendir,lx,ly,symm,name)
        commands += command
        if workdir != outdir:# sys_command ('cp '+latt+' '+outdir)
            commands += ['cp '+latt+' '+outdir]

        # Generate initial state
        initstate,command = genstate.init_state_commands (sytendir,fname,latt,name)
        commands += command
        if workdir != outdir:# sys_command ('cp '+initstate+' '+outdir)
            commands += ['cp '+initstate+' '+outdir]

    # Run DMRG
    H = read_H (fname)
    command = runDMRG (sytendir, latt, H, initstate, sweeps, name, cpus_dense, cpus_tensor, cpus_super, writeM,do_variance=False)
    commands += command
    if workdir != outdir:# sys_command ('cp '+workdir+'/*log '+outdir)
        commands += ['cp '+workdir+'/*log '+outdir]

    commands += ['rm *.cache']

    return commands, latt

if __name__ == '__main__':
    syten_envi (sys.argv)
    sytendir = os.environ['SYTENDIR']

    fname = sys.argv[1]
    commands, lattfile = dmrg_commands (fname, sytendir)
    for command in commands:
        print command
        os.system (command)

    exit()
    ##### measure pair-pair correlation
    name,lx,ly,Npar,Stot,symm,sweeps,workdir,outdir,cpus_dense,cpus_tensor,cpus_super,writeM = readparas (fname)
    meatmp = 'paircor.mea'

    x,y = 5,1

    ppairs,xyppair = x_pair_corr_sites (x,y,lx,ly)
    #ppairs,xyppair = all_pair_corr_sites (x,y,lx,ly) 
    gen_mea_file (ppairs,meatmp)    # generate the template file
    os.system ('cp '+meatmp+' '+outdir)

    sytenpydir = os.environ['SYTENPYDIR']
    psifiles = glob.glob('*.state')
    psifiles = sorted(psifiles,key=lambda i: int(i.split('_')[-2]))
    for psifile in psifiles:
        poutfile = outdir+'/'+psifile+'.paircorr'
        exe = 'python3 '+sytenpydir+'/pyten_paircorr.py lat='+lattfile+' psi='+psifile+' mea='+meatmp+' out='+poutfile+' threads_tensor='+str(cpus_tensor)
        print exe
        os.system (exe)
