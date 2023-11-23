set -m
client_num=5
exp_duration=60
burst_time=10
interfere=15

file_name=tmp_$(date +%Y%m%d%H%M%S)
touch file_name

for i in $(seq 1 1 $client_num); do
    python microbenchmark/test_multiclient_update.py large 114514 $PWD/$file_name > /dev/null &
    sleep 0.1
done

sleep 10
kill -10 $(ps | grep python | awk '{print $1}')
sleep 1

for j in $(seq 1 1 $exp_duration); do
    if [[ "$1" != "normal" ]]; then
        if [[ "$j" == "$burst_time" ]]; then
            echo $j
            curl -X POST -H "Content-Type: application/x-ndjson" http://localhost:9200/_bulk?pretty --data-binary @query/bulk_large_document.json | tail -n 20 &
        fi
        if [[ "$j" == "$interfere" ]]; then
            echo $j
            curl -X GET -H "Content-Type:application/json" --data-binary @query/boolean_search_interfere.json http://localhost:9200/_search > /dev/null &
        fi
    fi
    kill -10 $(ps | grep python | awk '{print $1}')
    sleep 1
done

kill -2 $(ps | grep python | awk '{print $1}')

python utils/data_read_and_draw.py $PWD/$file_name $client_num

rm -f $file_name
