from random_words import RandomWords, RandomNicknames
from faker import Faker
import random
import json
import httpx
import sys
sys.path.append('')

from utils.file_operation import create_file

def create_a_sentence(word_num, break_prob):
    first_word_creator = RandomNicknames()
    word_creator = RandomWords()
    
    title = first_word_creator.random_nick(gender="u")
    for _ in range(word_num):
        if random.random() < break_prob:
            title += ","
        title += " " + word_creator.random_word()
    
    title += random.sample([".", "!", "?", "~", ":)", ":(", "!!!", "^_^"], k=1)[0]
    return title + " "

def create_a_rubbish():
    word_num = random.randint(5, 20)
    sentence_num = random.randint(15, 50)
    break_prob = 0.2
    
    title = create_a_sentence(word_num, break_prob)
    
    article = ""
    for _ in range(sentence_num):
        article += create_a_sentence(word_num, break_prob)
    
    fake = Faker()
    
    return {"title": title, "content": article, "url": fake.url()}

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
    
    index="news"
    create_rubbish_num = 10
    
    create_rubbishes(f, client, HOST, index, create_rubbish_num)
    
    f.close()
    client.close()
