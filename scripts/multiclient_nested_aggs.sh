#!/bin/bash

set -m
client_num=$1
exp_duration=60
burst_time=10
interfere=12

search_indices=test10,test11,test12,test13,test14,test15,test16,test17,test18,test19,test20,test21,test22,test23,test24,test25,test26,test27,test28,test29
interfere_indices=test50
for i in {51..99}; do
	interfere_indices=$interfere_indices,test$i
done

file_name=tmp_$(date +%Y%m%d%H%M%S)

baseline=$(echo $4 | awk -F: '{print $1}')
baseline_info=($(echo $4 | awk -F: '{$1=""; print}'))
baseline_info_len=$(echo ${baseline_info[@]} | wc -w)

for i in $(seq 1 1 $client_num); do
    python microbenchmark/test_multiclient_search.py $PWD/$file_name $search_indices $PWD/${file_name}_${i} $PWD/${baseline_info[$(( (i - 1) % baseline_info_len ))]} &
    sleep 0.1
done

sleep 10

for j in $(seq 1 1 $exp_duration); do
    if [[ "$3" != "normal" ]]; then
        if [[ "$j" == "$burst_time" ]]; then
            echo $j
            start_us=$(date +"%s%6N")
            curl -X GET -H "Content-Type:application/json" --data-binary @${PWD}/query/nest_aggs.json http://localhost:9200/$search_indices/_search?pretty | tail -n 20 &
            end_us=$(date +"%s%6N")
            echo $(( end_us - start_us )) >> ${baseline_info[0]}
        fi
        if [[ "$j" == "$interfere" ]]; then
            echo $j
            start_us=$(date +"%s%6N")
            curl -X GET -H "Content-Type:application/json" --data-binary @query/boolean_search_interfere.json http://localhost:9200/$interfere_indices/_search?pretty | tail -n 5 &
            end_us=$(date +"%s%6N")
            echo $(( end_us - start_us )) >> ${baseline_info[0]}
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
