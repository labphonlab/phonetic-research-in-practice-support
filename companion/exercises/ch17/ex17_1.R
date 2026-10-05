# Exercise 17.1: Write the estimand and unit graph
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(readr); library(dplyr)
d <- read_tsv("companion/data/ch17/synthetic_regression/analysis_data.tsv", show_col_types = FALSE)
d |> summarise(tokens = n(), speakers = n_distinct(speaker_id), items = n_distinct(item_id))
d |> count(speaker_id, item_id, condition) |> count(n, name = "cells")  # tokens per cell
varies <- function(x, g) {
  mean(tapply(x, g, function(v) length(unique(v)) > 1))
}
sapply(c("speaker_id", "item_id"), function(g) {
  c(
    condition = varies(d$condition, d[[g]]),
    speaking_rate_z = varies(d$speaking_rate_z, d[[g]])
  )
})
