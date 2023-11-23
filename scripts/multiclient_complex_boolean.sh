set -m
client_num=5
exp_duration=60
burst_time_1=10
burst_time_2=20

file_name=tmp_$(date +%Y%m%d%H%M%S)
touch file_name

for i in $(seq 1 1 $client_num); do
    python microbenchmark/test_multiclient_search.py $PWD/$file_name &
    sleep 0.1
done

sleep 10

for j in $(seq 1 1 $exp_duration); do
    if [[ "$1" != "normal" ]]; then
        if [[ "$j" == "$burst_time_1" ]]; then
            echo $j
            curl -X GET -H "Content-Type:application/json" --data-binary @${PWD}/query/boolean_search.json "http://localhost:9200/*,-test2/_search?pretty" | tail -n 20 &
        fi
        if [[ "$j" == "$burst_time_2" ]]; then
            echo $j
            curl -X GET -H "Content-Type:application/json" --data-binary @${PWD}/query/boolean_search.json "http://localhost:9200/*,-test2/_search?pretty" | tail -n 20 &
        fi
    fi
    kill -10 $(ps | grep python | awk '{print $1}')
    sleep 1
done

kill -2 $(ps | grep python | awk '{print $1}')

python utils/data_read_and_draw.py $PWD/$file_name $client_num

rm -f $file_name
