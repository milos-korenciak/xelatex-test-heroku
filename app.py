#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main app running automatic reporting
@author: Milos.Korenciak@solargis.com"""


from __future__ import print_function  # Python 2 vs. 3 compatibility --> use print()
from __future__ import division  # Python 2 vs. 3 compatibility --> / returns float
from __future__ import unicode_literals  # Python 2 vs. 3 compatibility --> / returns float
from __future__ import absolute_import  # Python 2 vs. 3 compatibility --> absolute imports
import bottle
import datetime
import db
import os
import pickle
import tempfile
import shutil
import subprocess


app = bottle.default_app()  # bottle WSGI app object


class PdfCreationException(Exception):
    """The base class of exceptions in this app"""
    pass


class TempDirContext:
    """Context to create the temp dir to jail the data processed into"""
    def __enter__(self):
        # make a temp dir 
        self.tempdir = tempfile.mkdtemp()
        return self.tempdir

    def __exit__(self, exc_type, exc_val, exc_tb):
        # remove the temp dir
        shutil.rmtree(self.tempdir, ignore_errors=True)
        return (exc_type is None)  # True if everything is OK


def process_request_raw_to_2nd_level(task, tempdir=None,):
    """Transforms raw request to request level 2"""
    if not task.state < db.REQUEST_RAW:
        raise PdfCreationException("Task state is not enought to perform this processing")
    if not tempdir:  # if not run in tempdir, create one
        with TempDirContext() as tempdir:
            return process_request_raw_to_2nd_level(task, tempdir,)
    task.request_2nd_level = b""
    task.state = db.REQUEST_2ND_LEVEL
    task.save()


def process_request_2nd_level_to_tex_raw(task, tempdir=None,):
    """Transforms raw request to request level 2"""
    if not task.state < db.REQUEST_2ND_LEVEL:
        raise PdfCreationException("Task state is not enought to perform this processing")
    if not tempdir:  # if not run in tempdir, create one
        with TempDirContext() as tempdir:
            return process_request_2nd_level_to_tex_raw(task, tempdir,)
    task.tex_raw = b""
    task.state = db.TEX_RAW
    task.save()


def process_tex_raw_to_pdf_raw(task, tempdir=None):
    """Transforms raw request to request level 2"""
    if not task.state < db.TEX_RAW:
        raise PdfCreationException("Task state is not enought to perform this processing")
    if not tempdir:  # if not run in tempdir, create one
        with TempDirContext() as tempdir:
            return process_tex_raw_to_pdf_raw(task, tempdir,)

    print("I have tempdir: ", tempdir)
    tex_name = ""
    data = pickle.loads(task.tex_raw)
    for filename in data:
        if filename.endswith(".tex"):
            tex_name = filename
    assert tex_name.lower().endswith(".tex"), "No *.tex file given through Task id %s, timestamp %s"%(
        task.pdf_creation_id, task.datetime)

    os.environ["TEXMFLOCAL"] = "/app/buildpack/texmf-local"
    os.environ["TEXMFSYSCONFIG"] = "/app/buildpack/texmf-config"
    os.environ["TEXMFSYSVAR"] = "/app/buildpack/texmf-var"
    os.environ["TEXMFVAR"] = tempdir
    os.chdir(tempdir)

    BIN_PATH = os.environ.get("BIN_PATH", "/app/buildpack/bin/x86_64-linux/")  # we search for the xelatex binary
    XELATEX_PATH = os.path.join(BIN_PATH, "xelatex")
    print("I have XELATEX_PATH", XELATEX_PATH, " BIN_PATH", BIN_PATH)

    # compile
    subprocess.call(XELATEX_PATH + " --shell-escape -synctex=1 -interaction=nonstopmode %s"%tex_name, shell=True)

    output_pdf_name = tex_name[:-3] + "pdf"
    task.pdf_raw = open(output_pdf_name, "rb").read()
    task.state = db.PDF_RAW
    task.save()


def process_pdf_raw_to_pdf_signed(task, tempdir=None,):
    """Transforms raw pdf to signed pdf"""
    if not task.state < db.PDF_RAW:
        raise PdfCreationException("Task state is not enought to perform this processing")
    if not tempdir:  # if not run in tempdir, create one
        with TempDirContext() as tempdir:
            return process_pdf_raw_to_pdf_signed(task, tempdir,)
    task.pdf_signed = b""
    task.state = db.PDF_SIGNED
    task.save()


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
    task.tex_raw = pickle.dumps({"sample.tex", bottle.request.body.read()})
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
    task.state = db.PDF_RAW
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
    task.state = db.PDF_RAW
    task.save()
    return "Task accepted"


if __name__ == '__main__':
    bottle.run(host="", port=8080, debug=True, reloader=True)
