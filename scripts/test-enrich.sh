if [[ $1 == "create" ]]; then
  curl -X POST -H "Content-Type: application/json" http://localhost:9200/_bulk?pretty -d \
  '{ "index" : { "_index" : "mysource"} }
  { "my_number" : 1, "my_value" : "a" }
'
  sleep 1
  curl -X PUT -H "Content-Type: application/json" http://localhost:9200/_enrich/policy/myenrich_policy?pretty -d \
  '{
    "match": {
          "indices": "mysource",
          "match_field": "my_number",
          "enrich_fields": ["my_value"]
      }
  }'
  sleep 1
  curl -X POST http://localhost:9200/_enrich/policy/myenrich_policy/_execute?pretty
  sleep 1
  curl -X PUT -H "Content-Type: application/json" http://localhost:9200/_ingest/pipeline/myset_pipeline?pretty -d \
  '{
    "processors": [
      {
        "enrich": {
          "policy_name": "myenrich_policy",
          "field": "custom_id",
          "target_field": "enrich_value2"
        }
      },
      {
        "set": {
          "field": "my_set_field",
          "value": "foobar"
        }
      }
    ]
  }'
  sleep 1
  curl -X PUT -H "Content-Type: application/json" http://localhost:9200/_ingest/pipeline/myenrich_pipeline?pretty -d \
  '{
    "processors": [
      {
        "enrich": {
          "policy_name": "myenrich_policy",
          "field": "custom_id",
          "target_field": "enrich_value"
        }
      },
      {
        "pipeline": {
          "name": "myset_pipeline"
        }
      }
    ]
  }'
  sleep 1

  for i in {1..100}; do
    for j in {1..10}; do num=$((i*10+j)); curl -X POST -H "Content-Type: application/json" "http://localhost:9200/myindex/_doc/$num?pipeline=myenrich_pipeline&pretty" -d '{"custom_id" : "'$num'"}'; done &
  done
elif [[ $1 == "clean" ]]; then
  indices=$(curl -s -X GET http://localhost:9200/_cat/indices?v | grep open | awk '{print $3}')
  for indice in $indices; do
      curl -X DELETE http://localhost:9200/$indice?pretty
  done
  sleep 1
  curl -X DELETE http://localhost:9200/_ingest/pipeline/myenrich_pipeline?pretty
  sleep 1
  curl -X DELETE http://localhost:9200/_ingest/pipeline/myset_pipeline?pretty
  sleep 1
  curl -X DELETE http://localhost:9200/_enrich/policy/myenrich_policy?pretty
else
  echo "Usage 1: ./test-enrich.sh create"
  echo "Usage 2: ./test-enrich.sh clean"
fi
