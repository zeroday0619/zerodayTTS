#!/usr/bin/env bash

set -e
set -x

flake8 start.py app cogs
black start.py app cogs --check
isort start.py app cogs --check-only