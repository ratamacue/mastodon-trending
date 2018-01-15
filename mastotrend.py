#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Let's Mastodon"""

import json
from urllib.request import urlopen
import nltk  
from nltk.tokenize import TweetTokenizer
from nltk.stem.wordnet import WordNetLemmatizer 
from bs4 import BeautifulSoup
import string
import contractions
from nltk.corpus import stopwords
from functools import reduce
import pprint
# pipreqs --force .
# sudo python3 -m pip install -r requirements.txt

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

#timelineUrl = "https://mastodon.sdf.org/api/v1/timelines/public";

#data = json.load(urlopen(timelineUrl))

top_1000_words = set(line.strip() for line in open('topwords.txt'))
top_1000_words.update(["cannot", "e-mail"])



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
    def word_fix(word):
        word = word.lower()
        word = lemmatizer.lemmatize(word)
        return word
        
    lemmatizer = WordNetLemmatizer()
    tokenized = TweetTokenizer().tokenize(text)
    lemmatized = map(word_fix , tokenized)
    filtered = filter(lambda word: not word in top_1000_words, lemmatized)
    
    #print(tokenized)
    all_words = set(filtered) #the set prevents a single status from boosting a word multiple times.
    words_without_stopwords = filter(lambda w: len(w) > 4 and not w in set(stopwords.words('english')), all_words)
    words = words_without_stopwords
    
    return list(words)

def html_to_string (html):
    return words(contractions.fix(BeautifulSoup(html, "html.parser").get_text()))

big_list_of_words = reduce((lambda x,y: x+y), map(lambda status: html_to_string(status["content"]), data))
frequency_dist = nltk.probability.FreqDist(big_list_of_words)
pprint.pprint(frequency_dist.most_common(20))

