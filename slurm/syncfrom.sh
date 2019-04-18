#!/bin/bash

mySsh="ssh -p 22"
myOpt="-avzr --progress"
mySrc="ChiaMin.Chung@th-ws-e556.theorie.physik.uni-muenchen.de:/home/c/ChiaMin.Chung/bin/sub.*"
myTar="./"

rsync $myOpt -e "$mySsh" $mySrc $myTar



mySrc="ChiaMin.Chung@th-ws-e556.theorie.physik.uni-muenchen.de:/home/c/ChiaMin.Chung/sh/job*"

rsync $myOpt -e "$mySsh" $mySrc $myTar
