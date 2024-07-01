#!/bin/sh
# Formats source code.

isort client/ server/
black --line-length 80 client/ server/
