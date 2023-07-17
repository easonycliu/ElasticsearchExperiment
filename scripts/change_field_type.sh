index="test4"

curl -X PUT -H "Content-Type:application/json" --data-binary @query/index_mapping.json "localhost:9200/${index}_new" && \
python operations/update_all_doc_in_index.py $index && \
curl -X POST "localhost:9200/${index}/_refresh?pretty" && \
curl -X POST "localhost:9200/_reindex?pretty" -H 'Content-Type: application/json' -d '{"source": {"index": "'${index}'"},"dest": {"index": "'${index}'_new"}}' && \
curl -X POST "localhost:9200/${index}_new/_refresh?pretty" && \
curl -X DELETE "localhost:9200/${index}" && \
curl -X POST "localhost:9200/_reindex?pretty" -H 'Content-Type: application/json' -d '{"source": {"index": "'${index}'_new"},"dest": {"index": "'${index}'"}}' && \
curl -X POST "localhost:9200/${index}/_refresh?pretty" && \
curl -X DELETE "localhost:9200/${index}_new"