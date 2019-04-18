
def genlatt (sytendir,lx,ly,symm,name):
# symm can be 'su2' or 'u1'
    latt = name+'.lat'
    #if os.path.isfile(name):
    #    print 'Lattice already exists'
    #    return name

    command = sytendir+'/lat/syten-sql-mps-fermi-hubbard -l '+str(lx)+' -w '+str(ly)+' --sym '+symm+' -o '+latt

    commands  = ['echo','echo',"echo '* Generating lattice'"]
    commands += ['echo '+command, command]
    commands += ["echo '* Done generating lattice'",'echo']

    return latt, commands

