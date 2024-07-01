#!/bin/sh
# Drops database.

synchronizer/manage.py reset_db --noinput
