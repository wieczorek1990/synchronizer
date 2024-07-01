#!/bin/sh
# Installs dependencies.

pip install \
  -r client/requirements.txt \
  -r server/requirements.txt \
  -r requirements-development.txt
