# Exercise 18.2: Build a missingness map
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(readr); library(dplyr); library(tidyr); library(glmmTMB)
D <- "companion/data/ch18/synthetic_complex/"
f <- read_tsv(paste0(D, "trajectory_frames.tsv"), show_col_types = FALSE)
codes <- read_tsv(paste0(D, "missingness_codes.tsv"), show_col_types = FALSE)
# codes without a definition
setdiff(unique(f$availability_code), codes$availability_code)
f |>
  count(condition, availability_code) |>
  group_by(condition) |>
  mutate(prop = round(n / sum(n), 3)) |>
  select(-n) |>
  pivot_wider(names_from = condition, values_from = prop)
f$lost <- as.integer(f$availability_code != "observed")
# loss rate across speakers
range(tapply(f$lost, f$speaker_id, mean))
fit <- glmmTMB(
  lost ~ condition + time_normalized +
    (1 | speaker_id) + (1 | item_id),
  family = binomial, data = f
)
round(summary(fit)$coefficients$cond, 3)
f |>
  group_by(condition) |>
  summarise(
    complete_case = mean(measured_value, na.rm = TRUE),
    all_frames_true = mean(true_value)
  )
