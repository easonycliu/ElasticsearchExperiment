#!/bin/bash

set -m
client_num=$1
exp_duration=70
burst_time=10
abs_interval=15

search_indices=test10
for i in $(seq 11 1 90); do
    search_indices=$search_indices,test$i
done

file_name=tmp_$(date +%Y%m%d%H%M%S)

baseline=$(echo $4 | awk -F: '{print $1}')
baseline_info=($(echo $4 | awk -F: '{$1=""; print}'))
baseline_info_len=$(echo ${baseline_info[@]} | wc -w)
if [[ "$baseline_info_len" == "0" ]]; then
	baseline_info=("/dev/null")
fi

baseline_outputs=()
if [[ $baseline_info_len > 0 ]]; then
	for i in $(seq 1 1 $client_num); do
		baseline_outputs+=($PWD/${baseline_info[$(( (i - 1) % baseline_info_len ))]})
	done
fi

for i in $(seq 1 1 $client_num); do
    python microbenchmark/test_multiclient_search.py $PWD/$file_name test10 $PWD/${file_name}_${i} ${baseline_outputs[$i]} &
    sleep 0.1
done

sleep 10

for j in $(seq 1 1 $exp_duration); do
    if [[ "$3" != "normal" ]]; then
		if [[ "$(((j - burst_time) % abs_interval))" == "0" ]]; then
            echo $j
			bash -c 'start_us=$(date +"%s%6N") && curl -X GET -H "Content-Type:application/json" --data-binary @'${PWD}'/query/nest_aggs.json http://localhost:9200/'$search_indices'/_search?pretty | tail -n 20 && end_us=$(date +"%s%6N") && echo $(( end_us - start_us )) >> '${baseline_info[0]}'' &
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
