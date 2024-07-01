#!/bin/sh
# Runs synchronizer server.

synchronizer/manage.py migrate --noinput
synchronizer/manage.py collectstatic --noinput
synchronizer/manage.py runserver 0.0.0.0:80 --insecure
