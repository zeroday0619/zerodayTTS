#!/usr/bin/env bash

set -e
set -x

flake8 start.py configure.py app cogs
black start.py configure.py app cogs --check
isort start.py configure.py app cogs --check-only