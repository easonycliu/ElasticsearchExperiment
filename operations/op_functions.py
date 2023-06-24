from random_words import RandomWords, RandomNicknames
from faker import Faker
import random
import time
import json
import httpx
import sys
sys.path.append('')

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

def create_basic_content(origin_doc):
    word_num = random.randint(5, 20)
    sentence_num = random.randint(15, 50)
    break_prob = 0.2
    
    title = create_a_sentence(word_num, break_prob)
    
    article = ""
    for _ in range(sentence_num):
        article += create_a_sentence(word_num, break_prob)
    
    fake = Faker()
    
    return {"title": title, "content": article, "url": fake.url()}

def add_char_count(origin_doc):
    try:
        update_info = {"content_char_num": len(origin_doc["content"])}
    except KeyError:
        padding_string = "This is useless infomation, just for padding."
        update_info = {"content_char_num": len(padding_string), "content": padding_string}
    
    return update_info

def add_date_info(origin_doc):
    start_time = (2010, 1, 1, 0, 0, 0, 0, 0, 0)
    start_time_stamp = time.mktime(start_time)
    end_time_stamp = time.time()
    random_time = random.randint(int(start_time_stamp), int(end_time_stamp))
    time_touple = time.localtime(random_time)
    time_formated = time.strftime("%Y-%m-%d %H:%M:%S", time_touple)
    update_info = {"create_date": time_formated}
    return update_info

def toy_update(origin_doc):
    update_info = {"content_char_num": origin_doc["content_char_num"] + 1}
    return update_info

OPERATIONS = {
    "CREATE_BASIC_CONTENT": create_basic_content,
    "ADD_CHAR_COUNT": add_char_count,
    "ADD_DATE_INFO": add_date_info,
    "TOY_UPDATE": toy_update
}
