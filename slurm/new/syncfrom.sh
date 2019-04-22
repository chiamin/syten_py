#!/bin/bash
mySsh="ssh -p 61022"
myOpt="-avzr --progress"
myTar="./"
mySrc="chiaminchung@gateway.flatironinstitute.org"
myFiles="$myFiles $mySrc:/mnt/home/chiaminchung/.local/bin/*"
myFiles="$myFiles $mySrc:/mnt/home/chiaminchung/sub/*"

rsync $myOpt -e "$mySsh" $myFiles $myTar

