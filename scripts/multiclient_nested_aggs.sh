set -m
client_num=5
exp_duration=60
burst_time=10

search_indices=test10,test11,test12,test13,test14,test15,test16,test17,test18,test19,test20,test21,test22,test23,test24,test25,test26,test27,test28,test29

file_name=tmp_$(date +%Y%m%d%H%M%S)
touch file_name

for i in $(seq 1 1 $client_num); do
    python microbenchmark/test_multiclient_search.py $PWD/$file_name $search_indices &
    sleep 0.1
done

sleep 10

for j in $(seq 1 1 $exp_duration); do
    if [[ "$j" == "$burst_time" ]]; then
        echo $j
        curl -X GET -H "Content-Type:application/json" --data-binary @${PWD}/query/nest_aggs.json http://localhost:9200/$search_indices/_search?pretty | head -n 20 &
    fi
    kill -10 $(ps | grep python | awk '{print $1}')
    sleep 1
done

kill -2 $(ps | grep python | awk '{print $1}')

python utils/data_read_and_draw.py $PWD/$file_name $client_num

rm -f $file_name
