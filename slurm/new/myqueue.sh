#!/bin/bash
queues="gen ccq"
username=chiaminchung

for que in $queues; do
    squeue -u $username -p $que -o "%.7i %.8u %.40j %.9P %.2t %.9M %N %R %C"
    #lines=$(squeue -u chiamic -p mf_i-b2.8 -o "%.7i %.8u %.30j %.9P %.2t %.9M %N %R" | wc -l)
done
