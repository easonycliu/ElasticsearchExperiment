set -m
python microbenchmark/test_multithread_write.py &
sleep 60
kill -10 %1
python microbenchmark/test_sync_search.py &
sleep 10
python operations/create_rubbish_in_es.py news 1 true slow &
sleep 20
jobs
kill -2 %1
kill -2 %2
sleep 10
