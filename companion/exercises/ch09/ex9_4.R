# Exercise 9.4: Audit automation-induced bias
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# --- Part 1 of 2 ---
library(readr); library(dplyr); library(lme4); library(lmerTest)
a <- read_tsv("companion/data/ch09/synthetic_annotation/automatic_proposal_audit.tsv") |>
  mutate(kept = final_label == automatic_default_label,
         shift = abs(final_boundary_ms -
                       automatic_default_boundary_ms),
         mode_c = ifelse(annotation_mode == "correct_default", 0.5, -0.5),
         diff_c = ifelse(difficulty == "difficult", 0.5, -0.5))
a |> group_by(annotation_mode, difficulty) |>
  summarise(prop_kept = mean(kept), mean_shift = mean(shift), .groups = "drop")

# --- Part 2 of 2 ---
ctl <- glmerControl(optimizer = "bobyqa", optCtrl = list(maxfun = 2e5))
m1 <- glmer(
  kept ~ mode_c * diff_c + (1 | speaker_id),
  data = a, family = binomial, control = ctl
)
# lmerTest: REML, Satterthwaite df
m2 <- lmer(shift ~ mode_c * diff_c + (1 | speaker_id),
           data = a)
round(coef(summary(m1)), 2); round(coef(summary(m2)), 2)
VarCorr(m1); VarCorr(m2); c(isSingular(m1), isSingular(m2))
# Rule written beforehand: a variance of zero is reported, then the model is refit without that term
if (isSingular(m1)) round(coef(summary(glm(kept ~ mode_c * diff_c, data = a, family = binomial))), 2)
