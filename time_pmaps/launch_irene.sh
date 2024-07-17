#!/bin/bash

printf "WITH COMPRESSION AND NO INDEXING\n"

start=`date +%s`

city irene irene_Ar.conf

end=`date +%s`
let deltatime=end-start
let hours=deltatime/3600
let minutes=(deltatime/60)%60
let seconds=deltatime%60
printf "Time spent: %d:%02d:%02d\n" $hours $minutes $seconds
