import httpx
import json
import sys
sys.path.append('')

from utils.file_operation import create_file

HOST = "http://localhost:9200"

def get_all_id_in_index(client, host, index):
    id_list = []
    
    id_query = {
        "query": {
            "match_all": {}
        },
        "stored_fields": [],
        "size": 1
    }
    response = client.post(
        "{}/{}/_search?scroll=1m".format(host, index),
        content=json.dumps(id_query) + "\n",
        headers={"Content-Type": "application/json"}
    )
    
    response_json = response.json()
    while (len(response_json["hits"]["hits"]) > 0):
        scroll_id = response_json["_scroll_id"]
        id_list.extend([x["_id"] for x in response_json["hits"]["hits"]])
        scroll_query = {
            "scroll": "1m",
            "scroll_id": scroll_id
        }
        response = client.post(
            "{}/_search/scroll".format(host),
            content=json.dumps(scroll_query) + "\n",
            headers={"Content-Type": "application/json"}
        )
        response_json = response.json()
    
    return id_list

def update_method(origin_doc):
    try:
        update_info = {"content_char_num": len(origin_doc["_source"]["content"])}
    except KeyError:
        padding_string = "This is useless infomation, just for padding."
        update_info = {"content_char_num": len(padding_string), "content": padding_string}
    
    return update_info

if __name__ == "__main__":
    client = httpx.Client()
    f = create_file("response", "w")
    index = "test_4"
    
    id_list = get_all_id_in_index(client, HOST, index)
        
    for id in id_list:
        search_query = {
            "query": {
                "ids": {
                    "values": [id]
                }
            }
        }
        search_response = client.post(
            "{}/{}/_search".format(HOST, index, id),
            content=json.dumps(search_query) + "\n",
            headers={"Content-Type": "application/json"}
        )
        update_info = update_method(search_response.json()["hits"]["hits"][0])
        
        update_query = {
            "doc": update_info
        }
        update_response = client.post(
            "{}/{}/_update/{}".format(HOST, index, id),
            content=json.dumps(update_query) + "\n",
            headers={"Content-Type": "application/json"}
        )
        f.write("\nUpdate index {}.\nResponse = \n".format(index))
        json.dump(update_response.json(), f, indent=2)
    
    f.close()
    client.close()
    