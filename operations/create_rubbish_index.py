from elasticsearch import Elasticsearch

from create_rubbish_in_es import create_rubbishes

if __name__ == "__main__":
    es = Elasticsearch(
        "http://localhost:9200",
        basic_auth=("elastic", "o6qwdw_gcoUgCA4SALh2")
    )
    
    indexes = ["test_{}".format(x) for x in range(5)]
    for index in indexes:
        result = es.indices.create(index=index, ignore=400)
        create_rubbishes(es, index, create_rubbish_num=500)
        print("create indices result : {}".format(result))
        