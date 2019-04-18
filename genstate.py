# -*- coding: utf-8 -*-
import sys, os
from subprocess import check_output
from hamilt import xy_to_index
from readpara import read_para, read_Npar
from environ import syten_envi

def genRndState (sytendir,lat,Npar,Stot,symm,name,m=10):
    name += '.rnd.initstate'
    if symm == 'su2gc': Npar = ''
    #if os.path.isfile(name):
    #    print 'State already exists'
    #    return name

    command = sytendir+'/bin/syten-random -l '+lat+' -s '+str(Npar)+','+str(Stot)+' -m '+str(m)+' -o '+name

    commands  = ['echo','echo',"echo '* Generating random state'"]
    commands += ['echo '+command, command]
    commands += ["echo '* Done generating random state'",'echo']

    return name, commands

def get_lxly (sytendir,latt):
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

def genstateU1U1 (sytendir, latt, init, lx, ly, name):
# init = [[x1,y1,st1],...], where st can be '0', 'u', 'd', or '2'.
    name += '.U1U1.stripes.initstate'

    commands = []
    vac = 'vacuum.rnd'
    commands.append (sytendir+'/bin/syten-random -l '+latt+' -s 0,0.0 -m 1 -o '+vac)

    cdags = ''
    for x,y,st in init:
        ind = xy_to_index (x,y,lx,ly)
        if st == 'u':
            cdags += 'chu '+str(ind)+' @ * '
        elif st == 'd':
            cdags += 'chd '+str(ind)+' @ * '
        elif st == '2':
            cdags += 'cnd '+str(ind)+' @ * chu '+str(ind)+' @ * '
        elif st != '0':
            print 'Unknown local state on site(',x,y,'):',st
            raise Exception
    cdags = cdags.replace('* ','',1)

    commands.append (sytendir+'/bin/syten-apply-op -i '+vac+' -l '+latt+':"'+cdags+'" -o '+name)
    return name, commands

def genstateSU2U1 (sytendir, latt, init, lx, ly, name):
# init = [[x1,y1,st1],...], where st can be '0', '1', or '2'.
    psi = name+'.SU2U1.stripes.initstate'

    commands = [sytendir+'/bin/syten-random -g v -l '+latt+' -o '+psi]

    def apply_cdag (ind,N,S):
        N += 1
        if S == 0.5: S = 0
        elif S == 0: S = 0.5
        else:
            print 'Wrong totS:',S
            raise Exception
        command = sytendir+'/bin/syten-apply-op -l '+latt+':"ch '+str(ind)+' @" -s '+str(N)+','+str(S)+' -i '+psi+' -o '+psi
        return command, N, S

    N,S = 0,0.
    for x,y,st in init:
        ind = xy_to_index (x,y,lx,ly)
        if st == '1':
            command, N, S = apply_cdag (ind,N,S)
            commands.append (command)
        elif st != '0':
            print 'Unknown local state on site(',x,y,'):',st
            raise Exception
    return psi, commands


def read_init (fname):
    lx,ly = read_para (fname, ('lx','ly'), int, '=')
    Npar = read_Npar (fname)
    symm = read_para (fname, ('symm'), str, '=')
    typ,lines = 'None',[]
    with open(fname) as f:
        for line in f:
            if line.strip() == 'initState':
                for line in f:
                    if '}' in line: break
                    if 'type' in line:
                        typ = line.split()[-1]
                    else:
                        lines.append (line)
    return typ, lines, lx, ly, Npar, symm

def gen_init (typ, lines, lx, ly, Npar, symm):
    init = []
    if typ == 'vertical_stripes':

        if symm != 'su2' or symm != 'su2gc':
            print 'Error: symmetry',symm,'not yet support'
            raise Exception

        Np = 0
        def get_hx_hy (hx_key, hy_key):
            hx,hy = None,None
            for line in lines:
                if hx_key in line:
                    hx = map(int,line.split()[2:])
                elif hy_key in line:
                    hy = map(int,line.split()[2:])
            return hx, hy

        def get_hole_loc (hx, hy):
            loc = []
            for x in hx:
                for y in hy:
                    loc.append ([x,y])
            return loc
        # Get hole location
        hole_loc = []
        hx, hy = get_hx_hy ('hx =', 'hy =')
        hole_loc += get_hole_loc (hx, hy)
        hx, hy = get_hx_hy ('hx2 =', 'hy2 =')
        if hx != None and hy != None:
            hole_loc += get_hole_loc (hx, hy)

        # Set init
        for y in xrange(1,ly+1):
            for x in xrange(1,lx+1):
                if [x,y] in hole_loc:
                    st = '0'
                else:
                    st = '1'
                    Np += 1
                init.append ([x,y,st])
                print st,
            print

        if Np != Npar:
            print 'Number of particle not match:',Npar,Np
            raise Exception

    else:
        print 'Invalid type:',typ
        raise Exception
    return init

def init_state_commands (sytendir, fname, latt, name):

    typ, lines, lx, ly, Npar, symm = read_init (fname)
    if typ == 'None': # use random initial state
        Stot = read_para (fname, 'Stot', int, '=')
        name, commands = genRndState (sytendir, latt, Npar, Stot, symm, name)
    else:
        init = gen_init (typ, lines, lx, ly, Npar, symm)
        if len(init) != lx*ly:
            print 'Size not match'
            raise Exception
        if symm == 'u1':
            name, commands = genstateU1U1 (sytendir, latt, init, lx, ly, name)
        elif symm == 'su2':
            name, commands = genstateSU2U1 (sytendir, latt, init, lx, ly, name)
    return name, commands
