import os, sys, glob

mpss = glob.glob('*.state')
lat = glob.glob('*.lat')[0]
for mps in mpss:
    pair = mps+'.pair'
    if not os.path.exists (pair):
        os.system ('sub.syten.pair '+lat+' '+mps)
        print (mps)
