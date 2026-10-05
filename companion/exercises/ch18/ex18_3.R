# Exercise 18.3: Criticize a fitted model
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# --- Part 1 of 2 ---
library(readr); library(dplyr); library(mgcv); library(itsadug)
obs <- read_tsv(
  "companion/data/ch18/synthetic_complex/trajectory_frames.tsv",
  show_col_types = FALSE
) |>
  filter(availability_code == "observed") |>
  arrange(token_id, frame_index) |>
  mutate(
    across(c(speaker_id, item_id), factor),
    cond_o = factor(condition, levels = c("A", "B"), ordered = TRUE)
  )
contrasts(obs$cond_o) <- "contr.treatment"
obs$start.event <- !duplicated(obs$token_id)
fm <- measured_value ~ cond_o + s(time_normalized, k = 7) +
  s(time_normalized, by = cond_o, k = 7) +
  s(speaker_id, bs = "re") + s(item_id, bs = "re")
rho <- start_value_rho(bam(fm, data = obs, method = "fREML"))
fit <- function(x) {
  bam(fm, data = x, method = "fREML",
      rho = rho, AR.start = start.event)
}
grid <- expand.grid(
  time_normalized = seq(0, 1, 0.05),
  cond_o = factor(c("A", "B"), ordered = TRUE),
  speaker_id = NA,
  item_id = obs$item_id[1]
)
contrasts(grid$cond_o) <- "contr.treatment"

# --- Part 2 of 2 ---
focal <- function(m) {
  grid$speaker_id <- m$model$speaker_id[1]
  p <- predict(
    m, grid,
    exclude = c("s(speaker_id)", "s(item_id)")
  )
  mean(p[grid$cond_o == "B"] - p[grid$cond_o == "A"])
}
m <- fit(obs); r <- resid(m); tapply(r, obs$condition, sd)
c(
  full = focal(m),
  range(sapply(levels(obs$speaker_id), function(s) {
    focal(fit(droplevels(filter(obs, speaker_id != s))))
  }))
)
