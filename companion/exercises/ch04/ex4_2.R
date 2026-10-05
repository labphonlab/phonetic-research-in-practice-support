# Exercise 4.2: Repair an inconsistent open research plan
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(tidyverse)
plan <- read_tsv("plan_decisions.tsv", show_col_types = FALSE)
stopifnot(!any(plan$consent_covers_it == "no" & plan$tier == "public"))
plan |> filter(deviation_to_report == "yes") |> pull(promise)
