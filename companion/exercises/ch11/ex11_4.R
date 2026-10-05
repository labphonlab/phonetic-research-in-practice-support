# Exercise 11.4: Create a reconstructable normalization record
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(readr); library(dplyr)
root <- "companion/data/ch11/synthetic_segmental/"
man <- read_tsv(paste0(root, "segmental_measure_manifest.tsv"), col_types = cols(.default = col_character()))
est <- read_tsv(paste0(root, "acoustic_estimates.tsv"))
f1 <- man |> filter(measure_id == "f1") |> mutate(raw_value = est$f1_hz[match(token_id, est$token_id)])
ref <- f1 |> group_by(speaker_id) |> summarise(center = mean(raw_value), scale = sd(raw_value))
f1 <- left_join(f1, ref, by = "speaker_id") |>
  mutate(transformed_value = (raw_value - center) / scale)
identical((f1$raw_value - f1$center) / f1$scale, f1$transformed_value)
