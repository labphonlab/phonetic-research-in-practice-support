# Exercise 19.1: Rewrite a threshold conclusion
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# --- Part 1 of 2 ---
library(readr); library(dplyr); library(lme4); library(lmerTest); library(emmeans)
d <- read_tsv("companion/data/ch17/synthetic_regression/analysis_data.tsv", show_col_types = FALSE)
d$condition <- factor(d$condition, levels = c("BASE", "SHIFT_A", "SHIFT_B")); d$item_id <- factor(d$item_id)
m <- lmer(outcome ~ condition + speaking_rate_z + item_id + (condition | speaker_id), d)
em <- emmeans(m, ~ condition, at = list(speaking_rate_z = 0), weights = "equal")
res <- as.data.frame(confint(contrast(em, list(SHIFT_A_minus_BASE = c(-1, 1, 0), SHIFT_B_minus_BASE = c(-1, 0, 1)))))
print(res, digits = 3)
cat("speakers:", n_distinct(d$speaker_id), " items:", n_distinct(d$item_id), " rate z range:",
    round(range(d$speaking_rate_z), 1), " singular:", isSingular(m), " residual SD:", round(sigma(m), 2), "\n")

# --- Part 2 of 2 ---
sc <- read_tsv("companion/data/ch19/synthetic_claims/effect_scenarios.tsv", show_col_types = FALSE) |>
  filter(contrast_id == "SHIFT_A_minus_BASE")
for (i in seq_len(nrow(sc))) { set.seed(sc$seed[i]); se <- res$SE[1]
  est <- rnorm(sc$simulation_replicates[i], sc$true_effect_scenario[i], se); sig <- abs(est / se) > 1.96
  cat(sc$scenario_id[i], "power", round(mean(sig), 2), "Type S", round(mean(sign(est[sig]) != sign(sc$true_effect_scenario[i])), 3),
      "Type M", round(mean(abs(est[sig])) / abs(sc$true_effect_scenario[i]), 2), "\n") }
