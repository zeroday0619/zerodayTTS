#!/bin/sh -e
set -x

isort start.py app cogs --force-single-line-imports
autoflake --remove-all-unused-imports --recursive --remove-unused-variables start.py app cogs --exclude=__init__.py
black start.py app cogs
isort start.py app cogs