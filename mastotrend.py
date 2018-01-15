#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Let's Mastodon"""

import json
from urllib.request import urlopen
import nltk  
from nltk.tokenize import TweetTokenizer 
from bs4 import BeautifulSoup
import string
from nltk.corpus import stopwords
from functools import reduce
# pipreqs --force .
# sudo python3 -m pip install -r requirements.txt

nltk.download('stopwords')
nltk.download('punkt')

#timelineUrl = "https://mastodon.sdf.org/api/v1/timelines/public";

#data = json.load(urlopen(timelineUrl))



def getLotsOfToots():
    #Get a few pages of toots
    timelineUrl = "https://mastodon.sdf.org/api/v1/timelines/public?limit=40&"
    data = []
    paginator = ""
    for i in range(10):
        pagedUrl = timelineUrl+"&max_id="+paginator
        newData = (json.load(urlopen(pagedUrl)))
        paginator = newData[len(newData)-1]["id"]
        data = data + newData
    #print(data)
    return data
    
data = getLotsOfToots()    


def words(text):
    tokenized = TweetTokenizer().tokenize(text)
    #print(tokenized)
    all_words = set(TweetTokenizer().tokenize(text)) #the set prevents a single status from boosting a word multiple times.
    words_without_stopwords = filter(lambda w: len(w) > 4 and not w in set(stopwords.words('english')), all_words)
    words = words_without_stopwords
    
    return list(words)

def html_to_string (html):
    return words(BeautifulSoup(html, "html.parser").get_text())

big_list_of_words = reduce((lambda x,y: x+y), map(lambda status: html_to_string(status["content"]), data))
frequency_dist = nltk.probability.FreqDist(big_list_of_words)
print(frequency_dist.most_common(20))

