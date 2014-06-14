#!/bin/bash
source bin/activate
pip install -r requirements.txt
bower install
sass --no-cache --update --style compressed pubstompinfo/static/css/
alembic upgrade head
