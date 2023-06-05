from elasticsearch import Elasticsearch

es = Elasticsearch(
    "http://localhost:9200",
    basic_auth=("elastic", "o6qwdw_gcoUgCA4SALh2")
)

result = es.nodes.hot_threads()
print("hot_threads result : {}".format(result))

result = es.tasks.list()
print("tasks list result : {}".format(result))
