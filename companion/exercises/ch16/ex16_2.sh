#!/bin/sh
# Exercise 16.2: Replace a manual correction
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

git log --oneline -- source_measurements.tsv                # find the last unedited version
# bring it back
git restore --source=HEAD~1 -- source_measurements.tsv
# no output: identical to the original
git diff --stat HEAD~1 -- source_measurements.tsv
