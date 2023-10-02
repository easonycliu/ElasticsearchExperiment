set -m
python microbenchmark/test_sync_update.py large 114514 &
sleep 10
curl -X POST -H "Content-Type: application/x-ndjson" http://localhost:9200/_bulk?pretty --data-binary @query/bulk_large_document.json > /dev/null &
sleep 50
while true; do
    cancel_task=$(curl -s -X GET http://localhost:9200/_cat/tasks?v | grep 'bulk ' | awk '{print $2}' | sort | head -n 1)
    if [ -n "$cancel_task" ]; then
        echo $cancel_task
        curl -X POST http://localhost:9200/_tasks/$cancel_task/_cancel?pretty
        break
    fi
done
sleep 0
jobs
kill -2 %1
sleep 1
