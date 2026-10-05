#!/bin/sh
# Exercise 15.3: Audit forced alignment
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

mfa version
mfa align corpus_dir dictionary_path acoustic_model_path \
    aligned_dir
