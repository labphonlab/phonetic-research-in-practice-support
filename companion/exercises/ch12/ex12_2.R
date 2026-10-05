# Exercise 12.2: Compare time coordinates
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(readr); library(dplyr); library(tidyr); library(ggplot2)
root <- "companion/data/ch12/synthetic_prosody/"
rd <- function(f) read_tsv(paste0(root, f), col_types = cols())
fr <- rd("raw_frame_estimates.tsv") |>
  inner_join(rd("source_manifest.tsv"), by = "token_id") |>
  inner_join(rd("interval_manifest.tsv"), by = "token_id") |>
  inner_join(rd("landmarks.tsv"), by = "token_id") |>
  group_by(speaker_id) |>
  mutate(
    st = 12 * log2(
      selected_f0_hz / median(selected_f0_hz, na.rm = TRUE)
    )
  ) |>
  ungroup() |>
  filter(!is.na(st)) |>
  mutate(
    t_onset_ms = 1000 * (frame_time_s - interval_start_s),
    t_prop = t_onset_ms / duration_ms,
    t_landmark_ms = 1000 * (frame_time_s - landmark_time_s)
  )
fr |>
  pivot_longer(c(t_onset_ms, t_prop, t_landmark_ms),
               names_to = "coord", values_to = "t") |>
  ggplot(aes(t, st, colour = condition_id)) +
  geom_smooth(method = "gam", formula = y ~ s(x, k = 8)) +
  facet_wrap(~coord, scales = "free_x")
