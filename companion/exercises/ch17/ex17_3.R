# Exercise 17.3: Audit the random-effects path
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# --- Part 1 of 2 ---
library(readr); library(lme4); library(lmerTest); library(emmeans)
d <- read_tsv("companion/data/ch17/synthetic_regression/analysis_data.tsv", show_col_types = FALSE)
d$condition <- factor(d$condition, levels = c("BASE", "SHIFT_A", "SHIFT_B")); d$item_id <- factor(d$item_id)
f <- outcome ~ condition + speaking_rate_z + item_id
fits <- list(
  speaker_slope = lmer(
    update(f, . ~ . + (condition | speaker_id)),
    d,
    control = lmerControl(optimizer = "bobyqa")
  ),
  speaker_intercept = lmer(
    update(f, . ~ . + (1 | speaker_id)), d
  ),
  fixed_only = lm(f, d)
)

# --- Part 2 of 2 ---
max_cor <- function(m) { r <- attr(VarCorr(m)$speaker_id, "correlation")   # largest |correlation|
  if (is.null(r) || nrow(r) < 2) NA_real_ else max(abs(r[lower.tri(r)])) }
for (id in names(fits)) {
  m <- fits[[id]]; mer <- inherits(m, "merMod")
  ct <- summary(contrast(
    emmeans(
      m, ~ condition,
      at = list(speaking_rate_z = 0), weights = "equal"
    ),
    list(A_minus_BASE = c(-1, 1, 0))
  ))
  cat(
    id, "singular:", if (mer) isSingular(m) else NA,
    "max |cor|:", if (mer) round(max_cor(m), 3) else NA,
    "estimate:", round(ct$estimate, 2),
    "SE:", round(ct$SE, 2), "\n"
  )
}
print(VarCorr(fits$speaker_slope))
