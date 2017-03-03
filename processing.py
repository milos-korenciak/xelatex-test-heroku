#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The processing functions to be used by app and worker
@author: Milos.Korenciak@solargis.com"""


from __future__ import print_function  # Python 2 vs. 3 compatibility --> use print()
from __future__ import division  # Python 2 vs. 3 compatibility --> / returns float
from __future__ import unicode_literals  # Python 2 vs. 3 compatibility --> / returns float
from __future__ import absolute_import  # Python 2 vs. 3 compatibility --> absolute imports
import db
import io
import os
import pickle
import tempfile
import shutil
import subprocess


class PdfCreationException(Exception):
    """The base class of exceptions in this app"""
    pass


class TempDirContext:
    """Context to create the temp dir to jail the data processed into. It chdir into it temporarily"""
    def __enter__(self):
        # make a temp dir
        self.tempdir = tempfile.mkdtemp()
        self.actual_dir = os.getcwd()  # save original working dir
        os.chdir(self.tempdir)  # move to that temp dir
        return self.tempdir

    def __exit__(self, exc_type, exc_val, exc_tb):
        os.chdir(self.actual_dir)  # get to original working dir
        # remove the temp dir
        shutil.rmtree(self.tempdir, ignore_errors=True)  # TODO: FIX!!!
        return (exc_type is None)  # True if everything is OK


def process_request_raw_to_2nd_level(task, tempdir=None,):
    """Transforms raw request to request level 2"""
    if task.state != db.REQUEST_RAW:
        raise PdfCreationException("Task state is not enought to perform this processing")
    if not tempdir:  # if not run in tempdir, create one
        with TempDirContext() as tempdir:
            return process_request_raw_to_2nd_level(task, tempdir,)
    task.request_2nd_level = b""
    task.state = db.REQUEST_2ND_LEVEL
    task.save()


def process_request_2nd_level_to_tex_raw(task, tempdir=None,):
    """Transforms raw request to request level 2"""
    if task.state != db.REQUEST_2ND_LEVEL:
        raise PdfCreationException("Task state is not enought to perform this processing")
    if not tempdir:  # if not run in tempdir, create one
        with TempDirContext() as tempdir:
            return process_request_2nd_level_to_tex_raw(task, tempdir,)
    task.tex_raw = b""
    task.state = db.TEX_RAW
    task.save()


def process_tex_raw_to_pdf_raw(task, tempdir=None):
    """Transforms raw request to request level 2"""
    if task.state != db.TEX_RAW:
        raise PdfCreationException("Task state is not enought to perform this processing")
    if not tempdir:  # if not run in tempdir, create one
        with TempDirContext() as tempdir:
            return process_tex_raw_to_pdf_raw(task, tempdir,)

    print("I have tempdir: ", tempdir)
    tex_name = ""
    data = pickle.loads(task.tex_raw)
    for file_name, file_content in data.iteritems():
        with io.open(file_name, "wb") as fI:
            fI.write(file_content)
        if file_name.endswith(".tex"):
            tex_name = file_name
    assert tex_name.lower().endswith(".tex"), "No *.tex file given through Task id %s, timestamp %s"%(
        task.pdf_creation_id, task.datetime)

    os.environ["TEXMFLOCAL"] = "/app/buildpack/texmf-local"
    os.environ["TEXMFSYSCONFIG"] = "/app/buildpack/texmf-config"
    os.environ["TEXMFSYSVAR"] = "/app/buildpack/texmf-var"
    os.environ["TEXMFVAR"] = tempdir

    BIN_PATH = os.environ.get("BIN_PATH", "/app/buildpack/bin/x86_64-linux/")  # we search for the xelatex binary
    XELATEX_PATH = os.path.join(BIN_PATH, "xelatex")
    print("I have XELATEX_PATH", XELATEX_PATH, " BIN_PATH", BIN_PATH)
    for a, b, c in os.walk(tempdir):
        print("a, b, c", a, b, c)

    # compile
    subprocess.call(XELATEX_PATH + " --shell-escape -synctex=1 -interaction=nonstopmode %s"%tex_name, shell=True)
    for a, b, c in os.walk(tempdir):
        print("a, b, c", a, b, c)

    output_pdf_name = tex_name[:-3] + "pdf"
    task.pdf_raw = io.open(os.path.join(tempdir, output_pdf_name), "rb").read()
    task.state = db.PDF_RAW
    task.save()


def process_pdf_raw_to_pdf_signed(task, tempdir=None,):
    """Transforms raw pdf to signed pdf"""
    if task.state != db.PDF_RAW:
        raise PdfCreationException("Task state is not enought to perform this processing")
    if not tempdir:  # if not run in tempdir, create one
        with TempDirContext() as tempdir:
            return process_pdf_raw_to_pdf_signed(task, tempdir,)
    task.pdf_signed = b""
    task.state = db.PDF_SIGNED
    task.save()
