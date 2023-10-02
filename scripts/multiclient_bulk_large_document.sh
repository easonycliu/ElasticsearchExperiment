set -m
client_num=5
exp_duration=80
burst_time=10

file_name=tmp_$(date +%Y%m%d%H%M%S)
touch file_name

for i in $(seq 1 1 $client_num); do
    python microbenchmark/test_multiclient_update.py large 114514 $PWD/$file_name &
    sleep 0.1
done

sleep 10
kill -10 $(ps | grep python | awk '{print $1}')
sleep 1

for j in $(seq 1 1 $exp_duration); do
    if [[ "$j" == "$burst_time" ]]; then
        echo $j
        curl -X POST -H "Content-Type: application/x-ndjson" http://localhost:9200/_bulk?pretty --data-binary @query/bulk_large_document.json | head -n 20 &
    
    fi
    kill -10 $(ps | grep python | awk '{print $1}')
    sleep 1
done

kill -2 $(ps | grep python | awk '{print $1}')

python utils/data_read_and_draw.py $PWD/$file_name $client_num

rm -f $file_name
