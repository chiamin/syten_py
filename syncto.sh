#!/bin/bash

remote="ChiaMin.Chung@th-ws-e518.theorie.physik.uni-muenchen.de"
todir="/project/th-scratch/c/ChiaMin.Chung//code/mypy/sytendmrg/"
#remote="chiamic@gplogin1.ps.uci.edu"
#todir="/home/chiamic/mypy/syten"
#remote="ru32web@lxlogin8.lrz.de"
#todir="/home/hpc/uh3o1/ru32web/mypy/syten"
mySrc="./*.py"
myTar=$remote:$todir/

rsync -az --progress $mySrc $myTar
