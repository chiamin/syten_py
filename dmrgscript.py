from subprocess import call
import os, sys
from hamilt import HubH, localmuh, pairing_terms
import genstate
from readpara import read_para
from genlatt import genlatt
from environ import syten_envi

def genlatt (sytendir,lx,ly,symm,name,flags):
# symm can be 'su2' or 'u1'
    latt = name+'.lat'
    #if os.path.isfile(name):
    #    print 'Lattice already exists'
    #    return name

    command = sytendir+'/lat/syten-sql-mps-fermi-hubbard -l '+str(lx)+' -w '+str(ly)+' --sym '+symm+' -o '+latt+' '+flags

    commands  = ['echo','echo',"echo '* Generating lattice'"]
    commands += ['echo '+command, command]
    commands += ["echo '* Done generating lattice'",'echo']

    return latt, commands

def read_H (fname):
    lx,ly = read_para (fname, ('lx','ly'), int, '=')
    U  = read_para (fname, 'U', float, '=')
    t, mu, tp = read_para (fname, ('t','mu','tp'), float, '=', default=(1.,0.,0.))
    H = HubH (U, tp=tp, mu=mu, t=t)
    H += localmuh (fname)
    H += pairing_terms (fname)
    return H

def runDMRG (sytendir, latt, H, initState, sweeps, name, cpus_dense=1,cpus_tensor=1,cpus_super=1,writeM=1048576):
    flags  = ' --threads-dense '+str(cpus_dense)
    flags += ' --threads-tensor '+str(cpus_tensor)
    flags += ' --threads-super '+str(cpus_super)
    flags += ' --cache --cache-threshold '+str(writeM)
    flags += ' --local-expectations '+latt+':n '
    command = sytendir+'/bin/syten-dmrg '+flags+' -l '+latt+':"'+H+'" -i '+initState+' -s "'
    for m,Nswp,maxIter,cutoff,subspace,dmrgtype in sweeps:
        command += '(v '+dmrgtype+' m '+str(m)+' x '+str(2*Nswp)+' e { x '+str(maxIter)+' } eb '+str(subspace)+' t '+str(cutoff)+' convMinEnergyDiff -1 ) '
    command += '" -o '+name

    commands  = ['echo','echo',"echo '* Run DMRG'"]
    commands += echo_command (command)
    commands += ["echo '* Done DMRG'"]
    return commands

