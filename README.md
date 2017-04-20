## XeLaTeX reporting on heroku

This is work in progres for now.

At the end it should be full featured XeLaTeX reporting tool running on Heroku for Solargis2 project.
It will enable creating of semiautomatic + automatic .pdf reports for our customers.

The project responsible is Brano Cief. If something is not working, he knows who did it (bad) :-).

## Deploying locally

At first install
::

    pip install requirements.txt


You need to run *app.py*. It will start bottle webserver on port *8080* listening on *0.0.0.0* (= it will respond to requests from outer world also). So you need to open `http://127.0.0.1:8080 <http://127.0.0.1:8080>`.
The app has several enpoins serving:

1. */* [GET] - creation of dummy testing *.pdf*. Should excercise pdf creation from default .tex template.
2. */now/tex2pdf* [POST] - converts immediately binary posted .tex file --> .pdf. **Note 1: Images and other files may be missing! Note 2: The conversion must be done in 30 s in max. Else heroku kills the process!**

#. */now/tex2pdf_rich* [GET, POST] - converts immediately binary posted files (1 of them MUST be .tex!) into .pdf. YOu can post images also in multipart POST. **Note: The conversion must be done in 30 s in max. Else heroku kills the process!**
#. */enlist/tex2pdf_rich* [GET, POST] - enrolls the multipart POST for (later async) conversion into .pdf. Returns the task ID you can trace.
#. */enlist/get_state/{pdf_creation_id}* [GET] - gets the state of the task with given pdf_creation_id
#. */static/{jquery_file_name}* [GET] - statically seved jquery files (.js, .css) for testing purposes


## Deploying on heroku

You can directly deploy from git on heroku. To use Git - Heroku integration is recommended.
