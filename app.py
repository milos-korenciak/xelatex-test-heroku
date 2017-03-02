#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main app running automatic reporting
@author: Milos.Korenciak@solargis.com"""

import requests
import bottle
from rq import Queue
from worker import conn

def count_words_at_url(url):
    resp = requests.get(url)
    return len(resp.text.split())

q = Queue('default', connection=conn)

app = bottle.default_app()

@bottle.get("/")
def index():
    result = q.enqueue(count_words_at_url, 'http://heroku.com')
    print("result", result)
    return str(result.__dict__)


