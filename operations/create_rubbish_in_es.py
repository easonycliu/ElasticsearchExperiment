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

def fast_create_a_rubbish():
    doc = OPERATIONS["FAST_CREATE_BASIC_CONTENT"]({})
    doc.update(OPERATIONS["ADD_CHAR_COUNT"](doc))
    doc.update(OPERATIONS["ADD_DATE_INFO"]({}))
    return doc

def create_rubbishes(f, client, host, index, create_rubbish_num, refresh, creator):
    for iter in range(create_rubbish_num):
        if iter == int(create_rubbish_num * 0.9):
            print("Created {} documents".format(iter))
        data = creator()
        
        response = client.post("{}/{}/_doc?refresh={}".format(host, index, refresh),
                               content=json.dumps(data) + "\n",
                               headers={"Content-Type": "application/json"})
        
        f.write("\nCreate doc with id {}.\nResponse = \n".format(index))
        json.dump(response.json(), f, indent=2)

if __name__ == "__main__":
    client = httpx.Client()
    f = create_file("response", "w")
    HOST = "http://localhost:9200"
    
    index = "news" if len(sys.argv) < 2 else sys.argv[1]
    create_rubbish_num = 1000 if len(sys.argv) < 3 else int(sys.argv[2])
    refresh = "false" if len(sys.argv) < 4 else sys.argv[3]
    creator = create_a_rubbish if len(sys.argv) < 5 or (len(sys.argv) >= 5 and sys.argv[4] == "slow") else fast_create_a_rubbish
    
    create_rubbishes(f, client, HOST, index, create_rubbish_num, refresh, creator)
    
    f.close()
    client.close()
    print("Created {} rubbish documents in index {} using {} with{} refresh".format(create_rubbish_num, index, creator, "" if refresh == "true" else "out"))
