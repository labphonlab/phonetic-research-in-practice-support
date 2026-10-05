# Exercise 1.2: Initialize the capstone record
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(readr)
g <- read_tsv("gates.tsv", show_col_types = FALSE)
stopifnot(nrow(g) >= 3, !anyNA(g))
