import httpx
import json
import sys
sys.path.append('')

from utils.file_operation import create_file
from create_rubbish_in_es import create_rubbishes, create_a_rubbish

if __name__ == "__main__":
    f = create_file("response", "w")
    client = httpx.Client()
    HOST = "http://localhost:9200"
    
    indexes = ["test3"]
    for index in indexes:
        create_index_response = client.put("{}/{}".format(HOST, index))
        f.write("\nCreate index.\nResponse = \n")
        json.dump(create_index_response.json(), f, indent=2)
        create_rubbishes(f, client, HOST, index, create_rubbish_num=10000, refresh="false", creator=create_a_rubbish)
    
    client.close()
    f.close()
    