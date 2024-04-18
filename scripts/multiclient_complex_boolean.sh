#!/bin/bash

set -m
client_num=$1
exp_duration=70
burst_time_1=10
burst_time_2=20
abs_interval=30

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

half_indices=test10
for i in $(seq 11 1 70); do
    half_indices=$half_indices,test$i
done

for j in $(seq 1 1 $exp_duration); do
    if [[ "$3" != "normal" ]]; then
		if [[ "$(((j - burst_time_1) % abs_interval))" == "0" ]]; then
            echo $j
			bash -c 'start_us=$(date +"%s%6N") && curl -X GET -H "Content-Type:application/json" --data-binary @'${PWD}'/query/boolean_search_1.json http://localhost:9200/*,-test2,-test3,-test4/_search?pretty | tail -n 20 && end_us=$(date +"%s%6N") && echo $(( end_us - start_us )) >> '${baseline_info[0]}'' &
        fi
		if [[ "$(((j - burst_time_2) % abs_interval))" == "0" ]]; then
            echo $j
			bash -c 'start_us=$(date +"%s%6N") && curl -X GET -H "Content-Type:application/json" --data-binary @'${PWD}'/query/boolean_search_2.json http://localhost:9200/'$half_indices'/_search?pretty | tail -n 20 && end_us=$(date +"%s%6N") && echo $(( end_us - start_us )) >> '${baseline_info[0]}'' &
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
