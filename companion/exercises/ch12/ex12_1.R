# Exercise 12.1: Build a requested-frame table
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# --- Part 1 of 2 ---
library(readr); library(dplyr); library(tidyr)
root <- "companion/data/ch12/synthetic_prosody/"
iv <- read_tsv(paste0(root, "interval_manifest.tsv"))
raw <- read_tsv(paste0(root, "raw_frame_estimates.tsv"))
grid <- iv |> rowwise() |>
  reframe(
    token_id,
    frame_index = 0:floor(round(
      (interval_end_s - interval_start_s) / 0.01, 6)),
    frame_time_s = interval_start_s + frame_index * 0.01
  ) |>
  left_join(
    select(raw, token_id, frame_index, selected_f0_hz, frame_status),
    by = c("token_id", "frame_index")
  ) |>
  mutate(frame_status = replace_na(frame_status,
                                   "source_failure"))
cat("requested:", nrow(grid), " raw rows:", nrow(raw), "\n")
count(grid, frame_status)
tok <- grid |> group_by(token_id) |>
  summarise(requested = n(), usable = sum(!is.na(selected_f0_hz)))
cat("tokens with a non-usable frame:",
    sum(tok$usable < tok$requested), "of", nrow(tok), "\n")

# --- Part 2 of 2 ---
sm <- read_tsv(paste0(root, "source_manifest.tsv"))
grid |>
  left_join(select(sm, token_id, condition_id),
            by = "token_id") |>
  group_by(condition_id) |>
  summarise(
    requested = n(),
    missing_pct = round(100 * mean(is.na(selected_f0_hz)), 1)
  )
