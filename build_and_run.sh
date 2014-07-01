#!/bin/bash
source pubstomp-info/bin/activate
pip install -r requirements.txt
bower install
sass --no-cache --update --style compressed pubstompinfo/static/css/
alembic upgrade head
python manage.py runserver