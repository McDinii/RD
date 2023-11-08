#!/bin/bash

CMD poetry run python manage.py makemigrations && \
    poetry run python manage.py migrate && \
    poetry run python manage.py filltestdata && \
    poetry run gunicorn app.wsgi:application --bind 0.0.0.0:8000

