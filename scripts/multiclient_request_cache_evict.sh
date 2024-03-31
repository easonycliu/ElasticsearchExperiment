#!/bin/bash

set -m
client_num=$1
exp_duration=60
burst_time=10

file_name=tmp_$(date +%Y%m%d%H%M%S)

echo "Clear cache"
curl -s -X POST http://localhost:9200/_cache/clear?request=true > /dev/null

baseline=$(echo $4 | awk -F: '{print $1}')
baseline_info=($(echo $4 | awk -F: '{$1=""; print}'))
baseline_info_len=$(echo ${baseline_info[@]} | wc -w)

baseline_outputs=()
if [[ $baseline_info_len > 0 ]]; then
	for i in $(seq 1 1 $client_num); do
		baseline_outputs+=($PWD/${baseline_info[$(( (i - 1) % baseline_info_len ))]})
	done
fi

echo ${baseline_outputs[@]}

for i in $(seq 1 1 $client_num); do
    python microbenchmark/test_multiclient_request_cache.py true request_cache_evict $PWD/$file_name $PWD/${file_name}_${i} ${baseline_outputs[$i]} &
    sleep 0.1
done

sleep 10

for j in $(seq 1 1 $exp_duration); do
    if [[ "$3" != "normal" ]]; then
        if [[ "$j" == "$burst_time" ]]; then
            echo $j
            start_us=$(date +"%s%6N")
            curl -X GET -H "Content-Type: application/x-ndjson" "http://localhost:9200/request_cache_evict/_msearch?pretty&max_concurrent_searches=1" --data-binary @query/multi_search.json | tail -n 20 &
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
