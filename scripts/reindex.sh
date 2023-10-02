set -m
target_index=test1
burst_time=10
cancel_time=50
after_cancel=0
if [[ $1 == "write" ]]; then
    echo "use microbenchmark/test_multithread_write.py as victim client"
    python microbenchmark/test_multithread_write.py > /dev/null &
    sleep 10
    kill -10 %1
elif [[ $1 == "search" ]]; then
    echo "use microbenchmark/test_sync_search.py as victim client"
    python microbenchmark/test_sync_search.py > /dev/null &
else
    echo "usage 1: ./update_by_query.sh search"
    echo "usage 2: ./update_by_query.sh write"
    exit -1
fi
sleep $burst_time
echo "send reindex request"
curl -X POST -H Content-Type:application/json http://localhost:9200/_reindex?pretty -d '{"source": { "index": "'$target_index'" }, "dest": { "index": "'$target_index'-reindex" }}' &
sleep $cancel_time
echo "prepare cancel reindex request"
cancel_task=$(curl -s -X GET http://localhost:9200/_cat/tasks?v | grep reindex | awk '{print $2}')
if [ -n "$cancel_task" ]; then
    echo "cancel $cancel_task"
    curl -X POST http://localhost:9200/_tasks/$cancel_task/_cancel?pretty
fi
sleep $after_cancel
jobs
kill -2 %1
kill -2 %2
curl -X DELETE http://localhost:9200/$target_index-reindex
sleep 10
