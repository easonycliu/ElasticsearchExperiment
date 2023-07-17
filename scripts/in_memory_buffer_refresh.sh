set -m
python microbenchmark/test_sync_write.py &
python microbenchmark/test_sync_search.py &
sleep 10
python operations/create_rubbish_in_es.py  &
sleep 20
jobs
kill -2 %1
sleep 1