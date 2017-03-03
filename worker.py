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