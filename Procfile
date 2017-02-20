web: gunicorn --log-file=- -R --bind="0.0.0.0:$PORT" --debug app:app
heroku ps:scale web
