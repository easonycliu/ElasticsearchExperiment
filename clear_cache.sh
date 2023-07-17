indices="news"
for i in {1..100}; do
    indices="${indices},test${i}"
done
curl -X POST "http://localhost:9200/${indices}/_cache/clear?request=true"