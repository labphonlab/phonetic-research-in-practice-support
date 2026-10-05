# Exercise 12.4: Stress-test a rhythm claim
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(readr); library(dplyr)
s <- read_tsv("companion/data/ch12/synthetic_prosody/segmented_intervals.tsv")
npvi <- function(d)
  100 * mean(abs(diff(d)) /
               ((head(d, -1) + tail(d, -1)) / 2))
m <- s |>
  arrange(speaker_id, sentence_set, segmentation_profile,
          unit_index) |>
  group_by(sample_group, speaker_id, sentence_set,
           segmentation_profile) |>
  summarise(
    percent_v = 100 * sum(vowel_duration_ms) /
      sum(vowel_duration_ms + consonant_duration_ms),
    varco_v = 100 * sd(vowel_duration_ms) /
      mean(vowel_duration_ms),
    npvi_v = npvi(vowel_duration_ms), .groups = "drop"
  )
m |> filter(segmentation_profile == "primary") |>
  group_by(sample_group, sentence_set) |>
  summarise(npvi_v = round(mean(npvi_v), 1), .groups = "drop")
