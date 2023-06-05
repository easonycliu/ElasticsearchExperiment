import httpx
import json
import sys
sys.path.append('')

from utils.file_operation import create_file
from create_rubbish_in_es import create_rubbishes

if __name__ == "__main__":
    f = create_file("response", "w")
    client = httpx.Client()
    HOST = "http://localhost:9200"
    
    indexes = ["test_{}".format(x) for x in range(5)]
    for index in indexes:
        create_index_response = client.put("{}/{}".format(HOST, index))
        f.write("\nCreate index.\nResponse = \n")
        json.dump(create_index_response.json(), f, indent=2)
        create_rubbishes(f, client, HOST, index, create_rubbish_num=5)
    
    client.close()
    f.close()
    