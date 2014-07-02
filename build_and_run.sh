#!/bin/bash
source bin/activate
./build.sh
python manage.py runserver
