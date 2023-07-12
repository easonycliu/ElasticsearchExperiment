set -m
total_time=60
brust_time=10
cancel_after_brust=5
finish_after_cancel=40

echo "Start Benchmark Round ${i}"
curr_time="$(date +%Y%m%d%H%M%S)"

echo "Current Time is ${curr_time}"
python microbenchmark/test_sync_search.py $curr_time &
python microbenchmark/test_sync_search.py $curr_time "9201" &
python microbenchmark/test_sync_search.py $curr_time "9202" &
python microbenchmark/test_sync_search.py $curr_time "9203" &
sleep $brust_time
echo "Start Brust Client at ${brust_time} Second"
curl -X GET -H "Content-Type:application/json" --data-binary @${PWD}/query/nest_aggs.json http://localhost:9200/_search > /dev/null &
jobs
sleep $cancel_after_brust
# echo "Kill Brust Client after ${cancel_after_brust} Second"
# kill -2 %5
sleep $finish_after_cancel
echo "Kill Benchmark Client at ${total_time} Second"
kill -2 %1
kill -2 %2
kill -2 %3
kill -2 %4
sleep 5
jobs
