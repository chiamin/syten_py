#!/bin/bash

remote="chiaminchung@gateway.flatironinstitute.org"
todir="/mnt/home/chiaminchung/slurm"
mySrc="./*"
myTar=$remote:$todir/

echo "scp ./* $remote:$todir/"

#rsync -az --progress $mySrc $myTar
