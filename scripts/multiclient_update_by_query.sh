#!/bin/bash

set -m
client_num=$1
target_index_1=test3
target_index_2=test2
exp_duration=60
burst_time_1=10
burst_time_2=20

file_name=tmp_$(date +%Y%m%d%H%M%S)
touch $PWD/$file_name-sync

baseline=$(echo $4 | awk -F: '{print $1}')
baseline_info=($(echo $4 | awk -F: '{$1=""; print}'))
baseline_info_len=$(echo ${baseline_info[@]} | wc -w)

baseline_outputs=()
if [[ $baseline_info_len > 0 ]]; then
	for i in $(seq 1 1 $client_num); do
		baseline_outputs+=($PWD/${baseline_info[$(( (i - 1) % baseline_info_len ))]})
	done
fi

for i in $(seq 1 1 $client_num); do
    python microbenchmark/test_multiclient_write.py $PWD/$file_name $PWD/$file_name-sync $PWD/${file_name}_${i} ${baseline_outputs[$i]} &
    sleep 0.1
done

while [[ "$(wc -l $PWD/$file_name-sync | awk '{print $1}')" != "$client_num" ]]; do
    sleep 1
done

echo "Start normal workload"
kill -12 $(ps | grep python | awk '{print $1}')
sleep 5

for j in $(seq 1 1 $exp_duration); do
    if [[ "$3" != "normal" ]]; then
        if [[ "$j" == "$burst_time_1" ]]; then
            echo $j
            start_us=$(date +"%s%6N")
            curl -X POST -H "Content-Type: application/json" --data-binary @query/update_by_query.json "http://localhost:9200/$target_index_1/_update_by_query?refresh=true&pretty" | head -n 20 &
            end_us=$(date +"%s%6N")
            echo $(( end_us - start_us )) >> ${baseline_info[0]}
        fi
        if [[ "$j" == "$burst_time_2" ]]; then
            echo $j
            start_us=$(date +"%s%6N")
            curl -X POST -H "Content-Type: application/json" --data-binary @query/update_by_query.json "http://localhost:9200/$target_index_2/_update_by_query?refresh=true&pretty" | head -n 20 &
            end_us=$(date +"%s%6N")
            echo $(( end_us - start_us )) >> ${baseline_info[0]}
        fi
    fi
    kill -10 $(ps | grep python | awk '{print $1}')
    sleep 1
done

kill -2 $(ps | grep python | awk '{print $1}')

curl -X GET http://localhost:9200/$target_index_1,$target_index_2/_refresh

python utils/data_read_and_draw.py $PWD/$file_name $client_num $PWD/${2}_throughput
echo Latency > $PWD/${2}_latency
for i in $(seq 1 1 $client_num); do
    cat $PWD/${file_name}_${i} >> $PWD/${2}_latency
done

rm -f ${file_name}*

sleep 120
