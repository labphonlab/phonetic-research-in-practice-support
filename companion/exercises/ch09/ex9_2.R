# Exercise 9.2: Diagnose categorical agreement
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# --- Part 1 of 2 ---
library(readr); library(dplyr); library(tidyr); library(irr)
j <- read_tsv("companion/data/ch09/synthetic_annotation/categorical_judgments.tsv") |>
  filter(judgment_stage == "independent_first_pass")
w <- j |> select(item_id, speaker_id, annotator_id, label) |>
  pivot_wider(names_from = annotator_id, values_from = label)
agree <- function(d) c(
  pct = mean(d$SYN_RATER_A == d$SYN_RATER_B),
  kappa = kappa2(d[, c("SYN_RATER_A", "SYN_RATER_B")])$value
)
table(A = w$SYN_RATER_A, B = w$SYN_RATER_B)
round(agree(w), 2)

# --- Part 2 of 2 ---
set.seed(92); by_spk <- split(w, w$speaker_id)
boot <- replicate(2000, agree(bind_rows(
  by_spk[sample(names(by_spk), replace = TRUE)]
)))
round(apply(boot, 1, quantile, c(.025, .975)), 2)
both_modal <- which(w$SYN_RATER_A == "modal" & w$SYN_RATER_B == "modal")
thin <- w[-sample(both_modal, length(both_modal) %/% 2), ]
round(agree(thin), 2); table(thin$SYN_RATER_A)
