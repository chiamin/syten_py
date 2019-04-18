#!/bin/bash

mySsh="ssh -p 22"
myOpt="-avzr --progress"
myTar="./"

fromdir=/home/chiamic/hubbard_x4/16x4/pre
mySrc="$fromdir/*.in"
mySrc=$mySrc" $fromdir/h*.out"
mySrc=$mySrc" $fromdir/*.lat*"
mySrc=$mySrc" $fromdir/*.mem"
mySrc=$mySrc" $fromdir/*.envar"

#rsync $myOpt -e "$mySsh" $mySrc $myTar

#-----------------------

infile="h*.out"

echo $infile

sshdir=$(grep "Run Directory" $infile)
sshdir=$(echo ${sshdir##* })
#sshdir=$(echo $sshdir | sed -e 's/:/.cluster.theorie.physik.uni-muenchen.de:/g')

fromdir="chiamic@$sshdir"
mySrc="$fromdir/*log"
mySrc=$mySrc" $fromdir/*.lat*"
mySrc=$mySrc" $fromdir/*.hsz"
mySrc=$mySrc" $fromdir/*.state"

#echo "rsync $myOpt -e "$mySsh" $mySrc $myTar"
rsync $myOpt -e "$mySsh" $mySrc $myTar
