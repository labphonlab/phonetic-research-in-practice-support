# Exercise 17.4: Translate coefficients into claims
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(readr); library(dplyr); library(lme4); library(lmerTest); library(emmeans)
d <- read_tsv("companion/data/ch17/synthetic_regression/analysis_data.tsv", show_col_types = FALSE)
d$condition <- factor(d$condition, levels = c("BASE", "SHIFT_A", "SHIFT_B")); d$item_id <- factor(d$item_id)
m <- lmer(outcome ~ condition + speaking_rate_z + item_id + (condition | speaker_id), d)
em <- as.data.frame(emmeans(
  m, ~ condition | speaking_rate_z,
  at = list(speaking_rate_z = c(-4, -1.5, 0, 1.5, 4)),
  weights = "equal"
))
rng <- d |> group_by(condition) |> summarise(lo = min(speaking_rate_z), hi = max(speaking_rate_z))
em |>
  left_join(rng, by = "condition") |>
  mutate(
    supported = speaking_rate_z >= lo & speaking_rate_z <= hi
  ) |>
  select(condition, speaking_rate_z, emmean, SE, supported) |> print()
nd <- data.frame(condition = "BASE", speaking_rate_z = 0, item_id = "SYN_ITEM_01", speaker_id = "SYN_SPK_01")
c(
  observed_speaker = predict(m, nd),
  new_speaker = predict(m, nd, re.form = NA)
)
