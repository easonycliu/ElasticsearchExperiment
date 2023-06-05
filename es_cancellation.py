from elasticsearch import Elasticsearch

if __name__ == "__main__":
    es = Elasticsearch(
        "http://localhost:9200",
        basic_auth=("elastic", "o6qwdw_gcoUgCA4SALh2")
    )

    while True:
        result = es.tasks.list(actions="*reindex")
        if len(result["nodes"]) > 0:
            node_name = list(result["nodes"].keys())[0]
            task_name = list(result["nodes"][node_name]["tasks"].keys())[0]
            print("task name: {}, action: {}".format(task_name, result["nodes"][node_name]["tasks"][task_name]["action"]))
            if result["nodes"][node_name]["tasks"][task_name]["cancellable"]:
                print("cancel task {}".format(task_name))
                cancel_result = es.tasks.cancel(task_id=task_name)
                print("cancel task result: {}".format(cancel_result))
                break
        
        