# Exercise 19.3: Construct the conclusion map
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(readr); library(dplyr)
D <- "companion/outputs/ch14/02_sensitivity_universe/"
sp <- read_tsv(paste0(D, "specification_results.tsv"), show_col_types = FALSE)
fail <- read_tsv(paste0(D, "specification_failures.tsv"), show_col_types = FALSE)
prim <- sp$estimate[sp$configuration_id == "primary"]
map <- sp |>
  transmute(
    configuration_id, estimand,
    changes_estimand, exploratory,
    direction_agrees = sign(estimate) == sign(prim),
    estimate, ci_low, ci_high,
    within_5_to_10 = ci_low >= 5 & ci_high <= 10,
    speakers, diagnostic_status
  )
print(as.data.frame(map), digits = 3)
print(fail[, c("configuration_id", "failure_reason", "retained_in_denominator")])
filter(map, !changes_estimand, !exploratory) |>
  summarise(
    branches = n(), min = min(estimate), max = max(estimate)
  )
