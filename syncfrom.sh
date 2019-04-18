#!/bin/bash

remote="ChiaMin.Chung@th-ws-e518.theorie.physik.uni-muenchen.de"
fromdir="/project/th-scratch/c/ChiaMin.Chung//code/mypy/sytendmrg/"
#remote="ru32web@lxlogin8.lrz.de"
#fromdir="/home/hpc/uh3o1/ru32web/mypy/syten"
mySsh="ssh -p 22"
myOpt="-avzr --progress"
mySrc="$remote:$fromdir/*.py"
myTar="./"


rsync $myOpt -e "$mySsh" $mySrc $myTar
