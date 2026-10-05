# Exercise 4.1: Build a speech-data governance matrix
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(tidyverse)
gov <- read_tsv("governance_matrix.tsv", show_col_types = FALSE)
stopifnot(!anyNA(gov),
          all(gov$release_tier %in%
                c("public", "controlled", "closed")))
# must have no rows
gov |>
  filter(identifying_risk == "high", release_tier == "public")
