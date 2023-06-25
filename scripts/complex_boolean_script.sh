set -m
total_time=60
brust_time=10
cancel_after_brust_list=(2 5 10 15 20)
log_name="log_$(date +%Y%m%d%H%M%S)"

for cancel_after_brust in ${cancel_after_brust_list[*]}; do
    cancel_time=$((brust_time + cancel_after_brust))
    finish_after_cancel=$((total_time - cancel_time))
    file_name=()

    for i in {0..9}; do
        echo "Start Benchmark Round ${i}"
        curr_time="$(date +%Y%m%d%H%M%S)"
        file_name+=($curr_time)
        echo "Current Time is ${curr_time}"
        python microbenchmark/test_sync_search.py $curr_time &
        sleep $brust_time
        echo "Start Brust Client at ${brust_time} Second"
        curl -X GET -H "Content-Type:application/json" --data-binary @${PWD}/query/boolean_search.json http://localhost:9200/_search > /dev/null &
        jobs
        sleep $cancel_after_brust
        echo "Kill Brust Client at ${cancel_time} Second"
        kill -2 %2
        sleep $finish_after_cancel
        echo "Kill Benchmark Client at ${total_time} Second"
        kill -2 %1
        sleep 1

        curr_jobs=$(jobs)
        while [ -z "$curr_jobs" ]; do
            sleep 1
            curr_jobs=$(jobs)
        done
        
    done
    echo "${cancel_after_brust} ${file_name[*]}" >> "${PWD}/log/${log_name}"
done
