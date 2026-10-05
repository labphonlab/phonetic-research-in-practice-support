# Exercise 11.1: Build an event dictionary
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(readr); library(dplyr)
a <- read_tsv("companion/data/ch11/synthetic_segmental/annotation_manifest.tsv")
stops <- filter(a, token_class == "stop")
cat("closure before release:",
    sum(stops$closure_start_s < stops$release_s),
    "of", nrow(stops), "\n")
count(stops, ambiguity_code)
set.seed(11)
write_tsv(slice_sample(stops, n = 20) |> select(token_id),
          file.path(tempdir(), "blind_sample.tsv"))
