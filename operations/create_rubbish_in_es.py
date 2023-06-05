from random_words import RandomWords, RandomNicknames
from faker import Faker
import random
from elasticsearch import Elasticsearch

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

def create_rubbishes(es, index, create_rubbish_num):
    for _ in range(create_rubbish_num):
        data = create_a_rubbish()
        
        id = 0
        while (True):
            id = random.randint(0, 1000000000)
            is_exist = es.exists(index=index, id=id)
            print("check id {} exists in index {} result: {}".format(id, index, is_exist))
            if not is_exist:
                break
        
        print("create {} result : {}".format(index, es.create(index=index, id=id, document=data)))

if __name__ == "__main__":
    es = Elasticsearch(
        "http://localhost:9200",
        basic_auth=("elastic", "o6qwdw_gcoUgCA4SALh2")
    )
    index="news"
    create_rubbish_num = 10
    
    create_rubbishes(es, index, create_rubbish_num)
