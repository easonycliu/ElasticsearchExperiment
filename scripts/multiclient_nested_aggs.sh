#!/bin/bash

set -m
client_num=$1
exp_duration=60
burst_time=10
interfere=12

search_indices=test10,test11,test12,test13,test14,test15,test16,test17,test18,test19,test20,test21,test22,test23,test24,test25,test26,test27,test28,test29
interfere_indices=test50,test51,test52,test53,test54,test55,test56,test57,test58,test59,test60,test61,test62,test63,test64,test65,test66,test67,test68,test69,test70,test71,test72,test73,test74

file_name=tmp_$(date +%Y%m%d%H%M%S)

for i in $(seq 1 1 $client_num); do
    python microbenchmark/test_multiclient_search.py $PWD/$file_name $search_indices $PWD/${file_name}_${i} &
    sleep 0.1
done

sleep 10

for j in $(seq 1 1 $exp_duration); do
    if [[ "$3" != "normal" ]]; then
        if [[ "$j" == "$burst_time" ]]; then
            echo $j
            curl -X GET -H "Content-Type:application/json" --data-binary @${PWD}/query/nest_aggs.json http://localhost:9200/$search_indices/_search?pretty | tail -n 20 &
        fi
        if [[ "$j" == "$interfere" ]]; then
            echo $j
            curl -X GET -H "Content-Type:application/json" --data-binary @query/boolean_search_interfere.json http://localhost:9200/$interfere_indices/_search?pretty | tail -n 5 &
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
