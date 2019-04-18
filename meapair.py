import os, sys
from subprocess import check_output
from hsz import do_hsz
from envari import do_en_vari
from dmrg import read_H
from subprocess import call, check_output, STDOUT, CalledProcessError
from environ import syten_envi
from readpara import read_para_dict, read_lat, read_arg_dict, read_arg, get_flag, search_after

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

    # --- Read parameters ---
    dmrgout = sys.argv[1]
    para = read_para_dict (dmrgout, ('name','workdir','outdir','symm'), str, '=')
    para = read_para_dict (dmrgout, ('lx','ly','cpus_dense','cpus_tensor','cpus_super','writeM'), int, '=', para=para)
    para = read_arg_dict (sys.argv,['outdir','workdir','cpus_dense','cpus_tensor','cpus_super'],para=para)
    # para is a dict
    if para['symm'] != 'su2gc':
        print 'Error: symm is not su2gc:',para['symm']
        raise Exception
    for arg in sys.argv:
        if '-cpus_dense=' in arg:
            para['cpus_dense'] = int(arg.split('=')[-1])
        if '-cpus_tensor=' in arg:
            para['cpus_tensor'] = int(arg.split('=')[-1])
        if '-cpus_super=' in arg:
            para['cpus_super'] = int(arg.split('=')[-1])

    H = read_H (dmrgout)
    lat = read_lat (dmrgout)
    lat = para['workdir']+'/'+lat
    #print '# lattice:',lat
    psi_prefix = search_after (dmrgout,'syten-dmrg','-o').split('/')[-1]
    psi_files = (check_output('ls '+para['workdir']+'/'+psi_prefix+'*.state', shell=True)).split()
    psi_files = [psi.split('/')[-1] for psi in psi_files]
    swpn = [int(psi.split('_')[-2]) for psi in psi_files]
    psi_files = [x for _,x in sorted(zip(swpn,psi_files))]
    #print 'psi:',psi_files



    # --- Create commands ---
    #mea_out = para['outdir']+'/'+para['name']+'.pairing.mea'
    mea_out = os.getcwd()+'/'+para['name']+'.pairing.mea'
    '''if os.path.isfile (mea_out):
        f = open (mea_out)
        for line in f:
            if 'Done measuring pairing' in line:
                psi_files = [psi for psi in psi_files if psi not in line]'''


    flag = get_flag (writeM=para['writeM'], cpus_dense=para['cpus_dense'], cpus_tensor=para['cpus_tensor'], cpus_super=para['cpus_super'])
    try:
        print 'pairing measurements script:',mea_out
        f = open(mea_out,'w')
    except IOError:
        print 'Error: Can not open file:',mea_out
        raise Exception

    with f:
        f.write ('# lattice: '+lat+'\n')
        tmp = 'pairing.tmp'
        print 'pairing measurements template:',tmp
        for psi in psi_files:
            #psi_full = para['workdir']+'/'+psi
            psi_full = os.getcwd()+'/'+psi
            out_file = os.getcwd()+'/'+psi.strip('.state')+'.pairing.dat'
            make_tmp_pairing (tmp,para['lx'],para['ly'])
            f.write('\n'+sytendir+'/bin/syten-expectation '+flag+' --template-file '+tmp+' -l '+lat+' -a '+psi_full+' -r 1>'+out_file+'\n')
            f.write('\necho "Done measuring pairing on '+psi_full+'"\n')
