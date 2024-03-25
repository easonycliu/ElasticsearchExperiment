#!/bin/bash

set -m
client_num=$1
exp_duration=60
burst_time_1=10
burst_time_2=15

file_name=tmp_$(date +%Y%m%d%H%M%S)

for i in $(seq 1 1 $client_num); do
    python microbenchmark/test_multiclient_search.py $PWD/$file_name test10,test11,test12,test13,test14,test15,test16,test17,test18,test19 $PWD/${file_name}_${i} &
    sleep 0.1
done

sleep 10

for j in $(seq 1 1 $exp_duration); do
    if [[ "$3" != "normal" ]]; then
        if [[ "$j" == "$burst_time_1" ]]; then
            echo $j
            curl -X GET -H "Content-Type:application/json" --data-binary @${PWD}/query/boolean_search.json "http://localhost:9200/*,-test2,-test3,-test4/_search?pretty" | tail -n 20 &
        fi
        if [[ "$j" == "$burst_time_2" ]]; then
            echo $j
            curl -X GET -H "Content-Type:application/json" --data-binary @${PWD}/query/boolean_search.json "http://localhost:9200/*,-test2,-test3,-test4/_search?pretty" | tail -n 20 &
        fi
    fi
    kill -10 $(ps | grep python | awk '{print $1}')
    sleep 1
done

kill -2 $(ps | grep python | awk '{print $1}')

python utils/data_read_and_draw.py $PWD/$file_name $client_num $PWD/${2}_throughput
echo Latency > $PWD/${2}_latency
for i in $(seq 1 1 $client_num); do
    cat $PWD/${file_name}_${i} >> $PWD/${2}_latency
done

rm -f ${file_name}*

sleep 120
