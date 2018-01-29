#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Let's Mastodon"""

import json
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
# pipreqs --force .
# sudo python3 -m pip install -r requirements.txt
nltk.download('wordnet')
nltk.download('stopwords')

class MastoTrendData:
    lastTootSeen=None
    totalTootsExamined = 0
    frequency_dist = nltk.probability.FreqDist([])

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
    for i in range(10):
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
    return list(words_without_stopwords)

def html_to_string (html):
    return words(contractions.fix(BeautifulSoup(html, "html.parser").get_text()))

def tendProbability(hisoric_frequency_dist, history_toot_count, new_frequency_dist, new_toot_count):
    ret = {}
    for word in new_frequency_dist:
        try:
            historic_average = hisoric_frequency_dist[word]/history_toot_count
        except Exception:
            historic_average=0
        print("Historic word average "+word+" "+str(historic_average))
        new_average = new_frequency_dist[word]/new_toot_count
        ret[word] = new_average - historic_average
    return ret

def write_trending_json(sorted_probability_of_trending):
    trending_json = json.dumps(list(map(lambda item: item[0], sorted_probability_of_trending)))
    text_file = open("trending.json", "w")
    text_file.write(trending_json)
    text_file.close()

mastoTrendHistory = loadTrendData()
data = getLotsOfToots(mastoTrendHistory.lastTootSeen)

(max_toot_id,big_list_of_words) = reduce((lambda x,y: (max(x[0],y[0]), x[1]+y[1])), map(lambda status: (int(status["id"]), html_to_string(status["content"])), data), (0, []))
new_frequency_dist = nltk.probability.FreqDist(big_list_of_words)

probability_of_trending = tendProbability(mastoTrendHistory.frequency_dist, mastoTrendHistory.totalTootsExamined, new_frequency_dist, len(data))

sorted_probability_of_trending = sorted(probability_of_trending.items(), reverse=True, key=operator.itemgetter(1))[:10]

print("Last Toot: "+str(max_toot_id))
pprint.pprint(sorted_probability_of_trending)
write_trending_json(sorted_probability_of_trending)


#Save
mastoTrendHistory.frequency_dist = mastoTrendHistory.frequency_dist + new_frequency_dist
mastoTrendHistory.totalTootsExamined = mastoTrendHistory.totalTootsExamined + len(data)
mastoTrendHistory.lastTootSeen = max_toot_id
saveTrendData(mastoTrendHistory)
