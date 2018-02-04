#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Let's Mastodon"""

#TODO:  Maybe use TF-IDF instead http://www.nltk.org/api/nltk.html#nltk.text.TextCollection
# Example http://www.bogotobogo.com/python/NLTK/tf_idf_with_scikit-learn_NLTK.php
# Understandable Example http://billchambers.me/tutorials/2014/12/21/tf-idf-explained-in-python.html

import json
import io
import codecs
import pickle
import operator
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
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy #required by sklearn
import scipy  #required by sklearn

# pipreqs --force .
# sudo python3 -m pip install -r requirements.txt
nltk.download('wordnet')
nltk.download('stopwords')

class MastoTrendData:
    lastTootSeen=None
    history=[]


def loadTrendData():
    try:
        dataFile = open("mastotrend.dat","rb")
        return pickle.load(dataFile)
    except:
        print("Error loading mastotend.dat, starting over")
        return MastoTrendData()

def saveTrendData(mastoTrendData):
    dataFile = open("mastotrend.dat","wb")
    pickle.dump(mastoTrendData, dataFile)
    dataFile.close()


def getLotsOfToots(start):
    #Get a few pages of toots
    reader = codecs.getreader("utf-8")

    #timelineUrl = "https://mastodon.sdf.org/api/v1/timelines/public?limit=40"
    timelineUrl = "https://mastodon.social/api/v1/timelines/public?limit=40"
    data = []
    paginator = start
    for i in range(100):
        pagedUrl = timelineUrl if paginator is None else timelineUrl+"&since_id="+str(paginator)
        newData = json.load(reader(urlopen(pagedUrl)))
        if(len(newData) == 0 ): break
        paginator = newData[len(newData)-1]["id"]
        data = data + newData
    return data

def words(text):
    def word_fix(word):
        word = word.lower()
        word = lemmatizer.lemmatize(word)
        return word

    lemmatizer = WordNetLemmatizer()
    tokenized = TweetTokenizer().tokenize(text)
    lemmatized = map(word_fix , tokenized)
    all_words = set(lemmatized) #the set prevents a single status from boosting a word multiple times.
    words_without_stopwords = filter(lambda w: len(w) > 4 and not w in set(stopwords.words('english')), all_words)
    return " ".join(list(words_without_stopwords))

def html_to_string (html):
    return words(contractions.fix(BeautifulSoup(html, "html.parser").get_text()))


def write_trending_json(sorted_probability_of_trending):
    with io.open('trending.json', 'w', encoding='utf8') as json_file:
        json.dump(list(map(lambda item: item[0], sorted_probability_of_trending)), json_file, ensure_ascii=False)

mastoTrendHistory = loadTrendData()
#print (mastoTrendHistory.history)
data = getLotsOfToots(mastoTrendHistory.lastTootSeen)

(max_toot_id,new_documents) = reduce((lambda x,y: (max(x[0],y[0]), x[1]+[y[1]])), map(lambda status: (int(status["id"]), html_to_string(status["content"])), data), (0, []))
new_documents_as_one_document = [reduce(lambda x,y: x+y, new_documents)]

sklearn_tfidf = TfidfVectorizer(use_idf=True, sublinear_tf=True)

if(len(mastoTrendHistory.history) <1 ):
    print("Empty History.  Making a fake one.")
    mastoTrendHistory.history = new_documents_as_one_document #Is it bad that we are double-counting the first pass?

#fit_transform does a fit and a transform.  The fit part actually mutates the sklearn_tfidf.
print("Training with this many documents: "+str(len(mastoTrendHistory.history)))
sklearn_tfidf.fit(mastoTrendHistory.history)

print("Testing this many toots as one document: "+str(len(new_documents)))
tfidf_comparison_matrix = sklearn_tfidf.transform(new_documents_as_one_document)

#print(new_documents)
print(sklearn_tfidf.get_feature_names())
#print(len(tfidf_comparison_matrix.toarray()))

lists_of_lists = tfidf_comparison_matrix.toarray()
frequency_list = [sum(x) for x in zip(*lists_of_lists)]
#print(frequency_list)
words_list = sklearn_tfidf.get_feature_names()
#print(sklearn_tfidf.get_feature_names()[0]+ "=" +str(frequency_list[0] ))

results = [(words_list[i], frequency_list[i]) for i in range(len(words_list))]

sorted_results = sorted(results, key=lambda tup: tup[1], reverse=True)


print("Last Toot: "+str(max_toot_id))
pprint.pprint(sorted_results[:10])
write_trending_json(sorted_results[:10])


#Save
mastoTrendHistory.history = new_documents_as_one_document + mastoTrendHistory.history
mastoTrendHistory.lastTootSeen = max_toot_id
saveTrendData(mastoTrendHistory)
