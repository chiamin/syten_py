import os
from readpara import read_para

def syten_envi (argv):
    fname = argv[1]

    # Write memory usage
    jname = read_para (fname, 'name', str, '=')
    #os.environ['SYTEN_MEMORY_SAMPLER'] = jname+'.mem'

    #os.environ['SYTEN_DEFAULT_TPO_TRUNCATE'] = 'p'
    os.environ['SYTENDIR'] = os.environ['SYTENDIRREAL']

    symm = read_para (fname, 'symm', str, '=')
    if '-gc' in argv or symm == 'su2gc':
        os.environ['SYTENDIR'] = os.environ['SYTENDIRGCREAL']

    cplx = read_para (fname, 'complex', str, '=', ('no'))
    if '-cplx' in argv or cplx == 'yes':
        os.environ['SYTENDIR'] = os.environ['SYTENDIRCPLX']

