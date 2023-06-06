while true
do
	time curl -sS localhost:9200/_cat/tasks | awk '{print $1}' | sort | uniq -c
	sleep 1
done
