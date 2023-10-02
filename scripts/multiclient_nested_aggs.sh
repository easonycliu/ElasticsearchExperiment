set -m
client_num=5
exp_duration=60
burst_time=10

file_name=tmp_$(date +%Y%m%d%H%M%S)
touch file_name

for i in $(seq 1 1 $client_num); do
    python microbenchmark/test_multiclient_search.py $PWD/$file_name &
    sleep 0.1
done

sleep 10

for j in $(seq 1 1 $exp_duration); do
    if [[ "$j" == "$burst_time" ]]; then
        echo $j
        curl -X GET -H "Content-Type:application/json" --data-binary @${PWD}/query/nest_aggs.json http://localhost:9200/_search?pretty | head -n 20 &
    
    fi
    kill -10 $(ps | grep python | awk '{print $1}')
    sleep 1
done

kill -2 $(ps | grep python | awk '{print $1}')

python utils/data_read_and_draw.py $PWD/$file_name $client_num

rm -f $file_name
