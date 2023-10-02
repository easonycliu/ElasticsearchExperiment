set -m
echo "Clear cache"
curl -s -X POST http://localhost:9200/_cache/clear?request=true > /dev/null
echo "Start benchmark request cache"
python microbenchmark/test_multithread_request_cache.py $1 $2 &
sleep 10
echo "Start burst on index $2"
curl -X GET -H "Content-Type: application/x-ndjson" "http://localhost:9200/$2/_msearch?pretty&max_concurrent_searches=1" --data-binary @query/multi_search.json > /dev/null &
sleep 50
echo "cancel multi search request"
cancel_task=$(curl -s -X GET http://localhost:9200/_cat/tasks?v | grep msearch | awk '{print $2}')
if [ -n $cancel_task ]; then
    curl -X POST http://localhost:9200/_tasks/$cancel_task/_cancel?pretty
fi
sleep 0
jobs
kill -2 %1
sleep 1