# Exercise 18.1: Preserve or summarize a trajectory
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(readr); library(dplyr); library(lmerTest); library(mgcv); library(itsadug)
f <- read_tsv(
  "companion/data/ch18/synthetic_complex/trajectory_frames.tsv",
  show_col_types = FALSE
)
obs <- f |>
  filter(availability_code == "observed") |>
  arrange(token_id, frame_index) |>
  mutate(
    across(c(speaker_id, item_id), factor),
    cond_o = factor(condition, levels = c("A", "B"), ordered = TRUE)
  )
contrasts(obs$cond_o) <- "contr.treatment"
# first retained frame of each token
obs$start.event <- !duplicated(obs$token_id)
# midpoint benchmark
round(summary(lmer(
  measured_value ~ condition + (1 | speaker_id) + (1 | item_id),
  filter(obs, frame_index == 10)
))$coefficients, 2)
fm <- measured_value ~ cond_o + s(time_normalized, k = 7) +
  s(time_normalized, by = cond_o, k = 7) +
  s(speaker_id, bs = "re") + s(item_id, bs = "re")
m0 <- bam(fm, data = obs, method = "fREML")
rho <- start_value_rho(m0)
m1 <- bam(
  fm, data = obs, method = "fREML", rho = rho,
  AR.start = start.event
)
round(summary(m1)$s.table, 2)
round(c(
  rho = rho,
  lag1_before = acf_resid(m0, plot = FALSE)[2],
  lag1_after = acf_resid(m1, plot = FALSE)[2]
), 3)
