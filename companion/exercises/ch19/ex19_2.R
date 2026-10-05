# Exercise 19.2: Define a meaningful bound
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(readr); library(dplyr); library(lme4); library(lmerTest); library(emmeans)
d <- read_tsv(
  "companion/data/ch17/synthetic_regression/analysis_data.tsv",
  show_col_types = FALSE
)
d$condition <- factor(d$condition, levels = c("BASE", "SHIFT_A", "SHIFT_B"))
d$item_id <- factor(d$item_id)
m <- lmer(
  outcome ~ condition + speaking_rate_z + item_id +
    (condition | speaker_id),
  d
)
em <- emmeans(
  m, ~ condition,
  at = list(speaking_rate_z = 0), weights = "equal"
)
res <- as.data.frame(confint(contrast(em, list(
  SHIFT_A_minus_BASE = c(-1, 1, 0),
  SHIFT_B_minus_BASE = c(-1, 0, 1)
))))
b <- read_tsv(
  "companion/data/ch19/synthetic_claims/meaningful_bounds.tsv",
  show_col_types = FALSE
)
left_join(res, b, by = c("contrast" = "contrast_id")) |>
  mutate(verdict = case_when(
    lower.CL > upper_bound | upper.CL < lower_bound ~
      "difference beyond the bound",
    lower.CL >= lower_bound & upper.CL <= upper_bound ~
      "inside the bound (equivalence)",
    TRUE ~ "unresolved magnitude"
  )) |>
  select(
    contrast, estimate, lower.CL, upper.CL,
    lower_bound, upper_bound, verdict
  )
