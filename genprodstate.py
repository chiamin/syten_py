# -*- coding: utf-8 -*-
import sys, os
from dmrg import sys_command
from subprocess import check_output


def get_lxly (latt):
    command = sytendir+'/bin/syten-info '+latt
    dat = check_output(command, shell=True)
    dat = dat.rstrip().split('\n')
    for line in dat:
        if 'lattice on' in line:
            tmp = line.split()
            for word in tmp:
                if '\xc3' in word:
                    lx,ly = word.split('×')
                    try:
                        lx,ly = int(lx),int(ly)
                        return lx,ly
                    except ValueError:
                        pass
    print 'Cannot find lx and ly in',latt
    raise Exception

def genstateSU2U1 (sytendir, latt, init, name):
# init is a list of local state, which can be '0', 'u', 'd', or '2'.
    lx,ly = get_lxly (latt)
    if len(init) != lx*ly:
        print 'Size not match'
        raise Exception

    commands = []
    vac = 'vacuum.rnd'
    commands.append (sytendir+'/bin/syten-random -l '+latt+' -s 0,0.0 -m 1 -o '+vac)
    cdags = ''
    for i in xrange(len(init)):
        if init[i] == 'u':
            cdags += 'chu '+str(i)+' @ * '
        elif init[i] == 'd':
            cdags += 'chd '+str(i)+' @ * '
        elif init[i] == '2':
            cdags += 'cnd '+str(i)+' @ * chu '+str(i)+' @ * '
        elif init[i] != '0':
            print 'Unknown local state on site',i,':',init[i]
            raise Exception
    cdags = cdags.replace('* ','',1)

    out = name+'.rnd'
    commands.append (sytendir+'/bin/syten-apply-op -i '+vac+' -l '+latt+':"'+cdags+'" -o '+out)
    return commands

sytendir = os.environ['SYTENDIR']
commands = genstateSU2U1 (sytendir, sys.argv[1], ['u','d','u','d','0','u','d','u'],'gg')
for command in commands:
    sys_command (command)
