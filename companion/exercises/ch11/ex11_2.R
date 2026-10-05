# Exercise 11.2: Compare laryngeal cue representations
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(readr); library(dplyr); library(ggplot2)
root <- "companion/data/ch11/synthetic_segmental/"
st <- read_tsv(paste0(root, "annotation_manifest.tsv")) |> filter(token_class == "stop") |>
  left_join(read_tsv(paste0(root, "acoustic_estimates.tsv")), by = "token_id") |>
  mutate(vot_ms = 1000 * (voicing_onset_s - release_s),
         lead_ms = pmax(0, -vot_ms))
st |> group_by(context_id) |>
  summarise(n = n(), missing_vot = sum(is.na(vot_ms)),
            prop_lead = mean(vot_ms < 0, na.rm = TRUE),
            median_vot = median(vot_ms, na.rm = TRUE),
            median_f0 = median(f0_vowel_onset_hz))
ggplot(st, aes(vot_ms, f0_vowel_onset_hz,
               colour = context_id)) +
  geom_point(alpha = .5) +
  geom_vline(xintercept = 0, linetype = 2)
