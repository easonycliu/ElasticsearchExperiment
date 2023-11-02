set -m
client_num=5
target_index_1=test3
target_index_2=test2
exp_duration=60
burst_time_1=10
burst_time_2=20

file_name=tmp_$(date +%Y%m%d%H%M%S)
touch $file_name
touch $file_name-sync

for i in $(seq 1 1 $client_num); do
    python microbenchmark/test_multiclient_write.py $PWD/$file_name $PWD/$file_name-sync &
    sleep 0.1
done

while [[ "$(wc -l $PWD/$file_name-sync | awk '{print $1}')" != "$client_num" ]]; do
    sleep 1
done

kill -12 $(ps | grep python | awk '{print $1}')

for j in $(seq 1 1 $exp_duration); do
    if [[ "$j" == "$burst_time_1" ]]; then
        echo $j
        curl -X POST -H "Content-Type: application/json" --data-binary @query/update_by_query.json "http://localhost:9200/$target_index_1/_update_by_query?refresh=true&pretty" | head -n 20 &
    fi
    if [[ "$j" == "$burst_time_2" ]]; then
        echo $j
        curl -X POST -H "Content-Type: application/json" --data-binary @query/update_by_query.json "http://localhost:9200/$target_index_2/_update_by_query?refresh=true&pretty" | head -n 20 &
    fi
    kill -10 $(ps | grep python | awk '{print $1}')
    sleep 1
done

kill -2 $(ps | grep python | awk '{print $1}')

curl -X GET http://localhost:9200/$target_index_1,$target_index_2/_refresh

python utils/data_read_and_draw.py $PWD/$file_name $client_num

rm -f $file_name-sync
rm -f $file_name
