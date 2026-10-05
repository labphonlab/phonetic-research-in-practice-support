# Exercise 9.3: Analyze boundary differences
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# --- Part 1 of 2 ---
library(readr); library(dplyr); library(tidyr); library(ggplot2)
b <- read_tsv("companion/data/ch09/synthetic_annotation/boundary_judgments.tsv") |>
  select(item_id, speaker_id, condition, boundary_type, annotator_id, time_ms) |>
  pivot_wider(names_from = annotator_id, values_from = time_ms) |>
  mutate(diff = SYN_RATER_B - SYN_RATER_A)
b |> group_by(boundary_type, condition) |>
  summarise(n = n(), mean_signed = mean(diff), median_abs = median(abs(diff)),
            q05 = quantile(diff, .05), q95 = quantile(diff, .95), .groups = "drop")
ggplot(b, aes(diff)) + geom_histogram(bins = 30) + facet_grid(condition ~ boundary_type)

# --- Part 2 of 2 ---
# milliseconds, fixed before looking at the differences
tol <- c(strict = 5, loose = 20)
within <- function(d) d |> group_by(boundary_type, condition) |>
  summarise(strict = mean(abs(diff) <= tol["strict"]),
            loose = mean(abs(diff) <= tol["loose"]), .groups = "drop")
set.seed(93); by_spk <- split(b, b$speaker_id)
boot <- bind_rows(lapply(1:1000, function(i)
  within(bind_rows(
    by_spk[sample(names(by_spk), replace = TRUE)]
  ))
))
ci <- boot |> group_by(boundary_type, condition) |>
  summarise(across(c(strict, loose),
                   list(lo = ~quantile(.x, .025),
                        hi = ~quantile(.x, .975))), .groups = "drop")
left_join(within(b), ci, by = c("boundary_type", "condition"))
