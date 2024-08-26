#!/bin/sh
python3 manage.py collectstatic --noinput
#python manage.py makemigrations --merge --noinput
python3 manage.py migrate --noinput
uwsgi --ini uwsgi/uwsgi.${COMPOSE_PROJECT_NAME}.ini
