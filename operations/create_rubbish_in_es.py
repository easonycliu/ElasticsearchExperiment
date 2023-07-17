from random_words import RandomWords, RandomNicknames
from faker import Faker
import random
import json
import httpx
import sys
sys.path.append('')

from utils.file_operation import create_file
from operations.op_functions import OPERATIONS

def create_a_rubbish():
    doc = OPERATIONS["CREATE_BASIC_CONTENT"]({})
    doc.update(OPERATIONS["ADD_CHAR_COUNT"](doc))
    doc.update(OPERATIONS["ADD_DATE_INFO"]({}))
    return doc

def create_rubbishes(f, client, host, index, create_rubbish_num):
    for _ in range(create_rubbish_num):
        data = create_a_rubbish()
        
        response = client.post("{}/{}/_doc".format(host, index),
                               content=json.dumps(data) + "\n",
                               headers={"Content-Type": "application/json"})
        
        f.write("\nCreate doc with id {}.\nResponse = \n".format(index))
        json.dump(response.json(), f, indent=2)

if __name__ == "__main__":
    client = httpx.Client()
    f = create_file("response", "w")
    HOST = "http://localhost:9200"
    
    index = "news" if len(sys.argv) == 1 else sys.argv[1]
    create_rubbish_num = 1000
    
    create_rubbishes(f, client, HOST, index, create_rubbish_num)
    
    f.close()
    client.close()
    print("Created {} rubbish documents in index {}".format(create_rubbish_num, index))
