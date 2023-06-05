curl -X POST http://localhost:9200/_reindex?pretty -H 'Content-Type:application/json' -d '{"source":{"index":"news"},"dest":{"index":"news_v2"}}'
curl -X GET localhost:9200/_cat/indices?v
curl -X DELETE http://localhost:9200/news_v2
curl -X GET localhost:9200/_cat/indices?v