import os, sys, glob
from hamilt import HubH
from readpara import read_para

def do_en_vari (sytendir, lat, psi, H, cpus_dense=1,cpus_tensor=1,cpus_super=1,writeM=1048576):
    flag =  ' --cache --cache-threshold '+str(writeM)+' '
    flag += ' --threads-dense '+str(cpus_dense)+' '
    flag += ' --threads-tensor '+str(cpus_tensor)+' '
    flag += ' --threads-super '+str(cpus_super)+' '

    command = sytendir+'/bin/syten-error '+flag+' -l '+lat+':"'+H+'" -a '+psi

    #commands =  ['echo']
    commands = [command]
    return commands

def gen_en_var_script ():
    wdir = os.getcwd()
    lat = wdir+'/'+glob.glob('*.lat')[0]
    out = glob.glob('h*.out')[0]
    psi_files = sorted (glob.glob('*.state'), key=lambda i: int(i.split('_')[-2]))

    sytendir = os.environ['SYTENDIRREAL']
    exe = sytendir+'/bin/syten-dmrg '
    U = read_para (out, 'U', float, '=')
    tp = read_para (out, 'tp', float, '=')
    cpus = 20

    for psi in psi_files:
        psi = wdir+'/'+psi
        print ('echo '+psi)
        print ('SYTEN_MEMORY_SAMPLER=memsampley SYTEN_MEMORY_SAMPLER_SAMPLES=6000 SYTEN_MEMORY_SAMPLER_INTERVAL=10 '+exe+' -l '+lat+':"Hd '+str(U)+' * Ht 1.0 * + Htp '+str(tp)+' * +" -i '+psi+' -o '+psi+'.var -s "(v 2svar s false)" --log-level 6 --cache --log-file '+psi+'.var.log --threads-tensor '+str(cpus)+' --log-level-timings 6 --log-file-timings '+psi+'.var.timelog')

if __name__ == '__main__':
    gen_en_var_script ()
