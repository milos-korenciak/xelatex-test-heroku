#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The main app running automatic reporting
@author: Milos.Korenciak@solargis.com"""

import bottle
import datetime
import db
import os
import pickle
import tempfile
import shutil
import subprocess


app = bottle.default_app()  # bottle WSGI app object
db.database.initialize(db.connect(os.environ.get('DATABASE_URL') or 'sqlite:///default.db'))  # connect to DB
db.create_all_tables()  # silently ensure we have all tables we need


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
    """Transforms """
    if not tempdir:  # if not run in tempdir, create one
        with TempDirContext() as tempdir:
            return process_request_raw_to_2nd_level(task, tempdir,)
    task.request_2nd_level = ""
    task.state = "request_2nd_level"
    task.save()


def process_request_2nd_level_to_tex_raw(task, tempdir=None,):
    """Transforms """
    if not tempdir:  # if not run in tempdir, create one
        with TempDirContext() as tempdir:
            return process_request_2nd_level_to_tex_raw(task, tempdir,)
    task.request_2nd_level = ""
    task.state = "request_2nd_level"
    task.save()


def process_pdf_raw_to_pdf_signed(task, tempdir=None,):
    """Transforms """
    if not tempdir:  # if not run in tempdir, create one
        with TempDirContext() as tempdir:
            return process_pdf_raw_to_pdf_signed(task, tempdir,)
    task.request_2nd_level = ""
    task.state = "request_2nd_level"
    task.save()


def process_tex_raw_to_pdf_raw(task, tempdir=None):
    """Tansforms """
    tex_name = ""
    data = pickle.loads(task.tex_raw)
    for filename in data:
        if filename.endswith(".tex"):
            tex_name = filename
    assert tex_name.lower().endswith(".tex"), "No *.tex file given through Task id %s, timestamp %s"%(
        task.pdf_creation_id, task.datetime)
    if not tempdir:  # if not run in tempdir, create one
        with TempDirContext() as tempdir:
            return process_tex_raw_to_pdf_raw(task, tempdir)
    print("I have tempdir: ", tempdir)

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
    task.state = "request_2nd_level"
    task.locked_timestamp = datetime.datetime.now()
    task.save()
    # serve output

    bottle.response.content_type = 'application/pdf'
    return bottle.static_file(output_pdf_name, root=tempdir)


@db.database.atomic()
def get_task():
    """Lock the row of some not finished task."""
    tasks = db.PdfCreation.select(  # TODO:
            ).where((db.PdfCreation.locked_timestamp < datetime.datetime.now() - datetime.timedelta(0, 900)) |
               (db.PdfCreation.state < 5)
            ).order_by(db.PdfCreation.locked_timestamp).get()  # take the 1st only
    return tasks[0] if tasks else None


def worker():
    """Task performing all the heavy work"""
    # find all tasks to be done
    while 1:
        task = get_task()
        if not task:
            break
        with TempDirContext() as tempdir:
            if not task.request_2nd_level:
                process_request_raw_to_2nd_level(task, tempdir)
            if not task.tex_raw:
                process_request_2nd_level_to_tex_raw(task, tempdir)
            if not task.pdf_raw:
                process_tex_raw_to_pdf_raw(task, tempdir)
            if not task.pdf_signed:
                process_pdf_raw_to_pdf_signed(task, tempdir)


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
    pass


@bottle.post("/now/tex2pdf")
def serve_tex2pdf():
    """Immediately try to compile .tex --> .pdf"""
    with TempDirContext() as tempdir:
        # receive the custom .tex into the tempdir
        with open(os.path.join(tempdir, "sample.tex"), "wb") as sample_tex:
            buf = bottle.request.body.read()
            sample_tex.write(buf)
        print("I have written the sample.tex")
        task = db.PdfCreation()
        task.tex_raw = ""
        process_tex_raw_to_pdf_raw(task, tempdir=tempdir, tex_name="sample.tex")
        data = pickle.loads(task.pdf_raw)  # this is dictionary "filename":"filecontent"
        for k in data.iterkeys():
            if k.endswith(".pdf"):
                 return data[k]  # return filecontent of the first .pdf found
        raise Exception("Not found any *.pdf file in process_tex_raw_to_pdf_raw output!\n"
                        "Task id %s, timestamp %s"%(task.pdf_creation_id, task.datetime))


@bottle.post("/enlist/tex2pdf")
def serve_tex2pdf():
    """Enlist .tex for worker compilation to .pdf and signing"""
    files = bottle.request.files
    data = {k:v.read() for k,v in files.items()}
    db.PdfCreation(tex_raw=pickle.dumps(data), state="tex_raw").save()  # state = 3
    return "Task accepted"


if __name__ == '__main__':
    bottle.run(host="", port=8080, debug=True, reloader=True)
