# Exercise 11.3: Audit vowel normalization
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(readr); library(dplyr); library(tidyr)
root <- "companion/data/ch11/synthetic_segmental/"
v <- read_tsv(paste0(root, "annotation_manifest.tsv")) |> filter(token_class == "vowel") |>
  inner_join(read_tsv(paste0(root, "acoustic_estimates.tsv")), by = "token_id") |>
  inner_join(read_tsv(paste0(root, "split_manifest.tsv")), by = "speaker_id") |>
  filter(split == "training", annotation_status == "ok")
elig <- v |> count(speaker_id, vowel_category) |>
  pivot_wider(names_from = vowel_category, values_from = n, values_fill = 0) |>
  mutate(eligible = i >= 3 & a >= 3 & u >= 3)
w <- semi_join(v, filter(elig, eligible), by = "speaker_id") |> group_by(speaker_id) |>
  mutate(n_tok = n(), raw = f1_hz, log = log(f1_hz), z = (f1_hz - mean(f1_hz)) / sd(f1_hz),
         dF = f1_hz / mean(c(f1_hz, f2_hz / 3, f3_hz / 5))) |> ungroup()
a <- anova(lm(z ~ vowel_category + speaker_id, data = w))
round(a[["Sum Sq"]][1:2] / sum(a[["Sum Sq"]]), 3)
