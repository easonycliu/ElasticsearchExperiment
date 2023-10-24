set -m
target_index=test2
if [[ $1 == "write" ]]; then
    echo "use microbenchmark/test_multithread_write.py as victim client"
    python microbenchmark/test_multithread_write.py &
    sleep 100
    kill -10 %1
    echo Start sending
elif [[ $1 == "search" ]]; then
    echo "use microbenchmark/test_sync_search.py as victim client"
    python microbenchmark/test_sync_search.py > /dev/null &
else
    echo "usage 1: ./update_by_query.sh search"
    echo "usage 2: ./update_by_query.sh write"
    exit -1
fi
sleep 10
echo "send update-by-query request"
curl -X POST -H "Content-Type: application/json" --data-binary @query/update_by_query.json http://localhost:9200/$target_index/_update_by_query?refresh=true | head -n 10 &
sleep 50
echo "cancel update-by-query request"
cancel_task=$(curl -s -X GET http://localhost:9200/_cat/tasks?v | grep byquery | awk '{print $2}')
if [ -n $cancel_task ]; then
    curl -X POST http://localhost:9200/_tasks/$cancel_task/_cancel?pretty
fi
sleep 0
jobs
kill -2 %1
kill -2 %2
curl -X GET http://localhost:9200/$target_index/_refresh
sleep 5
