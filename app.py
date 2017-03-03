#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main app running automatic reporting
@author: Milos.Korenciak@solargis.com"""


from __future__ import print_function  # Python 2 vs. 3 compatibility --> use print()
from __future__ import division  # Python 2 vs. 3 compatibility --> / returns float
from __future__ import unicode_literals  # Python 2 vs. 3 compatibility --> / returns float
from __future__ import absolute_import  # Python 2 vs. 3 compatibility --> absolute imports
from processing import *
import bottle
import datetime
import os
import pickle
import subprocess


app = bottle.default_app()  # bottle WSGI app object


### WEB handlers
@bottle.get("/")
def get_index():
    # serve static webpage with JS
    print(os.environ)
    BIN_PATH = os.environ.get("BIN_PATH", "/app/buildpack/bin/x86_64-linux/")
    os.chdir(BIN_PATH)
    subprocess.call("./xelatex --shell-escape -synctex=1 -interaction=nonstopmode  brano2017-02-09_buildpack.tex", shell=True)
    bottle.response.content_type = 'application/pdf'
    return bottle.static_file("brano2017-02-09_buildpack.pdf", root='.')


@bottle.post("/")
def process_request():
    return "You probably wanted to call /now/tex2pdf or /now/tex2pdf_rich or /enlist/tex2pdf"


@bottle.post("/now/tex2pdf")
def serve_tex2pdf():
    """Immediately try to compile .tex --> .pdf"""
    task = db.PdfCreation()
    task.tex_raw = pickle.dumps({"sample.tex": bottle.request.body.read()})
    task.locked_timestamp = datetime.datetime.now()
    task.state = db.TEX_RAW
    task.save()
    process_tex_raw_to_pdf_raw(task)
    data = pickle.loads(task.pdf_raw)  # this is dictionary "filename":"filecontent"
    for k in data.iterkeys():
        if k.endswith(".pdf"):
             return data[k]  # return filecontent of the first .pdf found
    raise Exception("Not found any *.pdf file in process_tex_raw_to_pdf_raw output!\n"
                    "Task id %s, timestamp %s"%(task.pdf_creation_id, task.datetime))


@bottle.post("/now/tex2pdf_rich")
def serve_tex2pdf_rich():
    """Enlist .tex for worker compilation to .pdf and signing"""
    task = db.PdfCreation()
    files = bottle.request.files
    data = {k:v.read() for k, v in files.items()}
    task.tex_raw = pickle.dumps(data)
    task.locked_timestamp = datetime.datetime.now()
    task.state = db.TEX_RAW
    task.save()
    process_tex_raw_to_pdf_raw(task)
    data = pickle.loads(task.pdf_raw)  # this is dictionary "filename":"filecontent"
    for k in data.iterkeys():
        if k.endswith(".pdf"):
            return data[k]  # return filecontent of the first .pdf found
    raise Exception("Not found any *.pdf file in process_tex_raw_to_pdf_raw output!\n"
                    "Task id %s, timestamp %s" % (task.pdf_creation_id, task.datetime))
    return "Task accepted"


@bottle.post("/enlist/tex2pdf")
def enlist_tex2pdf():
    """Enlist .tex for worker compilation to .pdf and signing"""
    task = db.PdfCreation()
    files = bottle.request.files
    data = {k:v.read() for k, v in files.items()}
    task.tex_raw = pickle.dumps(data)
    task.state = db.TEX_RAW
    task.save()
    return "Task accepted"


if __name__ == '__main__':
    bottle.run(host="", port=8080, debug=True, reloader=True)
