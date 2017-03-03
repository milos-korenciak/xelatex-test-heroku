import os
import db
from app import process_request_raw_to_2nd_level, process_request_2nd_level_to_tex_raw, \
    process_tex_raw_to_pdf_raw, process_pdf_raw_to_pdf_signed, TempDirContext


if __name__ == '__main__':
    while 1:
        task = db.PdfCreation.get_locked_task()
        with TempDirContext() as tempdir:
            process_request_raw_to_2nd_level(task, tempdir=tempdir)
            process_request_2nd_level_to_tex_raw(task, tempdir=tempdir)
            process_tex_raw_to_pdf_raw(task, tempdir=tempdir)
            process_pdf_raw_to_pdf_signed(task, tempdir=tempdir)


    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()