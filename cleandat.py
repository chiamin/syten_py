import os
import subprocess as sp

def exe (command):
  #print command
  return sp.Popen(command, shell=True, stdout=sp.PIPE).communicate()[0]

def getid (username='ChiaMin.Chung'):
  ids = []
  queue = exe ('squeue -u '+username)
  lines = queue.split('\n')
  for line in lines:
    if username[:4] in line:
      jobid = line.split()[0]
      ids.append (jobid)
  return ids

def get_node_id (queues):
    dat = sp.check_output(('sinfo'))
    dat = dat.rstrip().split('\n')

    nodes = []
    for line in dat[1:]:
        tmp = line.split()
        queue = tmp[0]
        if queue in queues and 'down' not in line and 'drain' not in line:
            tmp = tmp[-1].rstrip(']').split(']')
            for nodestr in tmp:
                nodestr = nodestr.lstrip(',')

                if '[' not in nodestr:
                    if ',' not in nodestr:
                        nodes.append (nodestr)
                    else:
                        for node in nodestr.split(','):
                            nodes.append (node)
                    break

                prefix,idtmp = nodestr.split('[')

                if ',' in prefix:
                    ptmp = prefix.split(',')
                    for node in ptmp[:-1]:
                        nodes.append (node)
                    prefix = ptmp[-1]

                idstr = idtmp.split(',')
                for ids in idstr:
                    if '-' not in ids:
                        nodes.append (prefix+ids)
                    else:
                        ibeg,iend = map(int,ids.split('-'))
                        for i in xrange(ibeg,iend+1):
                            istr = str(i)
                            if i < 10: istr = '0'+istr
                            nodes.append (prefix+istr)

    #for i in nodes: print i
    return nodes

if __name__ == '__main__':

  workdir = '/data/ChiaMin.Chung/'

  jobs = getid()

  queues = ['TH-CL*']
  nodes = get_node_id (queues)

  sshsuf = '.cluster.theorie.physik.uni-muenchen.de'
  delsuf = '.cache'
  todel,runjobs=[],[]
  for node in nodes:
    node = node+sshsuf
    try: dirs = sp.check_output(('ssh',node,'ls',workdir),stderr=sp.STDOUT)
    except: dirs = ''
    if dirs == '':
      print 'In '+node+': ',workdir,'does not exist'
    else:
      print 'In '+node+': ',workdir+':'
      for dirr in dirs.split():
        #print '  ', dirr
        if dirr in jobs:
          print '  Jobs running: ', dirr
          runjobs.append ([node,dirr])
        else:
          try:
            delfiles = sp.check_output(('ssh',node,'ls',workdir+'/'+dirr+'/*'+delsuf),stderr=sp.STDOUT)
            print '  Trash in: ', dirr
            todel.append ([node, dirr])
          except:
            print '  No',delsuf,'file in',dirr
    exe ('exit')

  if len(todel) != 0:
    print
    print 'Running jobs:'
    for rr in runjobs: print '  ',rr[1]
    print 'Trash data:'
    for dd in todel: print '  ',dd[1]
    ifdel = raw_input ('Delete trash data? [y/n] ')
    if ifdel == 'y' or ifdel == 'Y':
      for node,dirr in todel:
        exestr = 'ssh '+node+' rm -r '+workdir+'/'+dirr+'/*'+delsuf
        print exestr
        os.system (exestr)
