set -m
echo "Start benchmark request cache"
python microbenchmark/test_multithread_request_cache.py &
sleep 10
echo "Start refresh"
curl -X POST http://localhost:9200/_cache/clear?request=true &
sleep 30
jobs
kill -2 %1
sleep 1