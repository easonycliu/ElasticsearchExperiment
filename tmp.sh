# set -m

# for i in {1..10}; do 
#     python microbenchmark/test_multithread_request_cache.py false request_cache_evict &
# done

# sleep 20

# kill -2 $(ps | grep python | awk '{print $1}')

exp_duration=60
burst_time=10

for i in $(seq 1 1 $exp_duration); do
    if [[ "$i" == "$burst_time" ]]; then
        echo $i
    fi
done