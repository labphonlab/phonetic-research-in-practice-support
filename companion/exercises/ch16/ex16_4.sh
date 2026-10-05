#!/bin/sh
# Exercise 16.4: Perform a clean-room run
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install -r companion/requirements-python.txt
python3 -m pip freeze > environment_clean.txt
