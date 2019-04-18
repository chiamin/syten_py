#!/bin/bash

wdir=$PWD
latt=$(ls *.lat)
psidir=/beegfs/SCRATCH/white/chiamic/5703508/
psifiles=$(ls $psidir/*.state | xargs -n 1 basename)
cpus=10
writeM=8388608

python ~/mypy/syten/paircorr.py -auto
pairmea=$(ls *.paircor.mea)

for psifile in $psifiles; do
    echo "/home/chiamic/syten/bin/syten-expectation -l $wdir/$latt --template-file $wdir/$pairmea -a $psidir/$psifile --threads-tensor $cpus --cache --cache-threshold $writeM >> $wdir/$psifile.paircorr"
done
