#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Let's Mastodon"""

import json
from urllib.request import urlopen
import nltk   
from bs4 import BeautifulSoup
import string
from functools import reduce
# pipreqs --force .
# sudo python3 -m pip install -r requirements.txt

timelineUrl = "https://mastodon.sdf.org/api/v1/timelines/public";

data = json.load(urlopen(timelineUrl))

def words(text):
    words = text.split()
    return list(words)

def html_to_string (html):
    return words(BeautifulSoup(html, "html.parser").get_text())

big_list_of_words = reduce((lambda x,y: x+y), map(lambda status: html_to_string(status["content"]), data))
frequency_dist = nltk.probability.FreqDist(big_list_of_words)
print(frequency_dist.most_common(20))

