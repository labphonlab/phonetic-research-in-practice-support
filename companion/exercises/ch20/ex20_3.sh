#!/bin/sh
# Exercise 20.3: Assemble and audit a release candidate
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

rm -rf derived && python3 route.py public \
  && shasum -a 256 derived/summary_public.tsv \
  > expected_artifacts.txt
rm -rf derived && python3 route.py public \
  && shasum -a 256 -c expected_artifacts.txt
# versions behind the clean run
(python3 --version; python3 -m pip freeze) > environment_record.txt
