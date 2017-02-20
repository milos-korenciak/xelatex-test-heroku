web: gunicorn --log-file=/tmp/logfile.log -R --bind="0.0.0.0:$PORT" --debug app:app
heroku ps:scale web
