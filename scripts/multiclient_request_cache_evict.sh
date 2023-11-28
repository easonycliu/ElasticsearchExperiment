#!/bin/bash

set -m
client_num=$1
exp_duration=60
burst_time=10

file_name=tmp_$(date +%Y%m%d%H%M%S)

echo "Clear cache"
curl -s -X POST http://localhost:9200/_cache/clear?request=true > /dev/null

for i in $(seq 1 1 $client_num); do
    python microbenchmark/test_multiclient_request_cache.py true request_cache_evict $PWD/$file_name $PWD/${file_name}_${i} &
    sleep 0.1
done

sleep 10

for j in $(seq 1 1 $exp_duration); do
    if [[ "$3" != "normal" ]]; then
        if [[ "$j" == "$burst_time" ]]; then
            echo $j
            curl -X GET -H "Content-Type: application/x-ndjson" "http://localhost:9200/request_cache_evict/_msearch?pretty&max_concurrent_searches=1" --data-binary @query/multi_search.json > /dev/null &
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
