#!/bin/bash

while [[ $# -gt 0 ]]
do
key="$1"
case $key in
    -all|--sync_more_files)
    SYNCALL=true
    shift # past argument
    ;;
    --default)
    shift
    ;;
    *)
            # unknown option
    shift
    ;;
esac
done



infile=$(ls -d -- *.out | grep -v '^slurm')
echo $infile

sshdir=$(grep "Run Directory" $infile)
sshdir=$(echo ${sshdir##* })
sshdir=$(echo $sshdir | sed -e 's/:/.cluster.theorie.physik.uni-muenchen.de:/g')


mySsh="ssh -p 22"
myOpt="-avzr --progress"
fromdir="ChiaMin.Chung@$sshdir"
mySrc="$fromdir/*log"
mySrc=$mySrc" $fromdir/*.hsz"
mySrc=$mySrc" $fromdir/*.mea"
mySrc=$mySrc" $fromdir/*.err"
if [ "$SYNCALL" = true ]; then
    mySrc=$mySrc" $fromdir/*.lat"
    mySrc=$mySrc" $fromdir/*.state"
fi
myTar="./"

rsync $myOpt -e "$mySsh" $mySrc $myTar

