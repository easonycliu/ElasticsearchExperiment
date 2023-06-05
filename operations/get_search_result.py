import json
import os
import time
import httpx
import sys
sys.path.append('')

from utils.file_operation import create_file

HOST = "http://localhost:9200"
client = httpx.Client()
f = create_file("response", "a")

create_index_response = client.put("{}/news".format(HOST))
f.write("Create new index.\nResponse = \n")
json.dump(create_index_response.json(), f, indent=2)

data = {"title": "Save your life from boring works.", "content": "It's bullshitting.", "url": "https://google.com"}
create_doc_response = client.post("{}/news/_doc".format(HOST), 
                                  content=json.dumps(data) + "\n", 
                                  headers={"Content-Type": "application/json"})
f.write("\nCreate new document.\nResponse = \n")
json.dump(create_doc_response.json(), f, indent=2)

query = {
    "query": {
        "match": {
            "content" : "life"
        }
    }
}

for x in range(5):
    search_response = client.post("{}/news/_search?from=0&size=1000".format(HOST),
                                  content = json.dumps(query) + "\n",
                                  headers={"Content-Type": "application/json"})
    f.write("\nSearch.\nResponse = \n")
    json.dump(search_response.json(), f, indent=2)
    
f.close()
client.close()
