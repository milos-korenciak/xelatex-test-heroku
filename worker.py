#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Automatic reports worker
@author: Milos.Korenciak@Solargis.com"""

from __future__ import print_function  # Python 2 vs. 3 compatibility --> use print()
from __future__ import division  # Python 2 vs. 3 compatibility --> / returns float
from __future__ import unicode_literals  # Python 2 vs. 3 compatibility --> / returns float
from __future__ import absolute_import  # Python 2 vs. 3 compatibility --> absolute imports
import db
import time
from app import process_request_raw_to_2nd_level, process_request_2nd_level_to_tex_raw, \
    process_tex_raw_to_pdf_raw, process_pdf_raw_to_pdf_signed, TempDirContext, PdfCreationException


if __name__ == '__main__':
    while 1:
        task = db.PdfCreation.get_locked_task()
        if task is None:
            print("going to sleep 20 sec")
            time.sleep(20)
            continue
        with TempDirContext() as tempdir:
            print("tempdir: {}, task.id {}".format(tempdir, task.pdf_creation_id))
            try:
                process_request_raw_to_2nd_level(task, tempdir=tempdir)
            except PdfCreationException as e:
                print(e)
            try:
                process_request_2nd_level_to_tex_raw(task, tempdir=tempdir)
            except PdfCreationException as e:
                print(e)
            try:
                process_tex_raw_to_pdf_raw(task, tempdir=tempdir)
            except PdfCreationException as e:
                print(e)
            try:
                process_pdf_raw_to_pdf_signed(task, tempdir=tempdir)
            except PdfCreationException as e:
                print(e)
            print("end of task ;-)")
