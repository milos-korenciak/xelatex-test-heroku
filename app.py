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
            bottle.response.content_type = "application/pdf"
            return data[k]  # return filecontent of the first .pdf found
    raise Exception("Not found any *.pdf file in process_tex_raw_to_pdf_raw output!\n"
                    "Task id %s, timestamp %s"%(task.pdf_creation_id, task.datetime))


HTML_UI_TEX2PDF_RICH = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
<title>Heroku .tex + images to .pdf compiler</title>
<head>
  <meta charset="UTF-8">
  <link rel="stylesheet" href="/static/jquery-ui.css">
  <script src="/static/jquery-1.12.4.js"></script>
  <script src="/static/jquery-ui.js"></script>
</head>
<body>


<form action="tex2pdf_rich" method="post" enctype="multipart/form-data">
  tex file: <input type="file" name="sample.tex" /> <br / >
  <div id="newFilesDiv">
  </div>
  <input type="submit" /> <br / >
</form>
<a href="javascript: addFile()"><button id="addFile" type="button">+++ Add new file +++</button></a>
<script type="text/javascript">
fileCount = 1;
function addFile() {
    var newFilesDiv = $("#newFilesDiv");
    newFilesDiv.append('next file No. '+fileCount+': <input type="file" name="'+fileCount+'.dat" /> <br / >');
    fileCount +=1;
}
</script>
</body>
</html>"""


@bottle.get("/now/tex2pdf_rich")
def web_tex2pdf_rich():
    """Static web for sending .tex +other files to convert to pdf"""
    return HTML_UI_TEX2PDF_RICH


@bottle.post("/now/tex2pdf_rich")
def serve_tex2pdf_rich():
    """Enlist .tex for worker compilation to .pdf and signing"""
    task = db.PdfCreation()
    files = bottle.request.files
    data = {v.raw_filename: v.file.read() for v in files.values()}
    task.tex_raw = pickle.dumps(data)
    task.locked_timestamp = datetime.datetime.now()
    task.state = db.TEX_RAW
    task.save()
    process_tex_raw_to_pdf_raw(task)
    data = pickle.loads(task.pdf_raw)  # this is dictionary "filename":"filecontent"
    for k in data.iterkeys():
        if k.endswith(".pdf"):
            bottle.response.content_type = "application/pdf"
            return data[k]  # return filecontent of the first .pdf found
    raise Exception("Not found any *.pdf file in process_tex_raw_to_pdf_raw output!\n"
                    "Task id %s, timestamp %s" % (task.pdf_creation_id, task.datetime))
# ### How to test from commandline:
# curl  -X POST
# -F "brano2017-02-09_buildpack.tex=@/home/l/tmp__/buildpack/bin/x86_64-linux/brano2017-02-09_buildpack.tex"
# -F "overview_map.png=@/home/l/tmp__/buildpack/bin/x86_64-linux/overview_map.png"
# -F "myfigure.png=@/home/l/tmp__/buildpack/bin/x86_64-linux/myfigure.png"
# -o brano2017-02-09_buildpack.pdf
# https://xelatex-test.herokuapp.com/now/tex2pdf_rich


@bottle.get("/enlist/tex2pdf_rich")
def enlist_tex2pdf_rich():
    """Static web for sending .tex +other files to convert to pdf"""
    return HTML_UI_TEX2PDF_RICH


@bottle.post("/enlist/tex2pdf_rich")
def enlist_tex2pdf():
    """Enlist .tex for worker compilation to .pdf and signing"""
    task = db.PdfCreation()
    files = bottle.request.files
    data = {v.raw_filename: v.file.read() for v in files.values()}
    task.tex_raw = pickle.dumps(data)
    task.state = db.TEX_RAW
    task.save()
    return "Task id {} accepted".format(task.pdf_creation_id)


@bottle.get("/enlist/get_state/<pdf_creation_id>")
def get_task_state(pdf_creation_id=None):
    """Gets sate of the requested task"""
    try:
        task = db.PdfCreation.get(pdf_creation_id=pdf_creation_id)
        return str(task.state)
    except (AttributeError, db.pw.DoesNotExist) as e:
        print("Occured: ", e)
        return "Such task does not exists"


@bottle.route('/static/<filename:path>')
def static_files(filename):
    if not filename.startswith("jquery"):
        return ""
    return bottle.static_file(filename, root='.')


if __name__ == '__main__':
    bottle.run(host="", port=8080, debug=True, reloader=True)
