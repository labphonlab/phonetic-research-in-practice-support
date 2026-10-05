# Exercise 17.2: Recode the same question
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(readr)
d <- read_tsv("companion/data/ch17/synthetic_regression/analysis_data.tsv", show_col_types = FALSE)
d$condition <- factor(d$condition, levels = c("BASE", "SHIFT_A", "SHIFT_B"))
cc <- read_tsv("companion/data/ch17/synthetic_regression/condition_contrasts.tsv", show_col_types = FALSE)
cust <- as.matrix(cc[cc$coding_id == "custom_A_vs_BASE_B_vs_mean", c("column_1", "column_2")])
codings <- list(treatment = contr.treatment(3), sum = contr.sum(3), custom = cust)
fits <- lapply(codings, function(k) { contrasts(d$condition) <- k; lm(outcome ~ condition, d) })
round(sapply(fits, coef), 2)                          # intercept and coefficients differ
all.equal(fitted(fits$treatment), fitted(fits$custom)) # fitted means do not
