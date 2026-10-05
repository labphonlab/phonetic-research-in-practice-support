# Exercise 8.3: Separate sensitivity and criterion
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# --- Part 1 of 2 ---
suppressMessages({library(readr); library(dplyr)})
ev <- read_tsv("companion/data/ch08/synthetic_perception/detection_event_log.tsv", show_col_types = FALSE)
sdt <- ev |>
  group_by(condition_id) |>
  summarise(H = sum(signal_present == 1 & yes_response == 1), S = sum(signal_present == 1),
            FA = sum(signal_present == 0 & yes_response == 1), N = sum(signal_present == 0),
            pc = mean(correct)) |>
  # loglinear correction
  mutate(hit = (H + 0.5) / (S + 1), fa = (FA + 0.5) / (N + 1),
         dprime = qnorm(hit) - qnorm(fa),
         criterion = -(qnorm(hit) + qnorm(fa)) / 2)
print(sdt |> mutate(across(c(pc, hit, fa, dprime, criterion), \(x) round(x, 2))))

# --- Part 2 of 2 ---
suppressMessages(library(lme4))
# +0.5 = signal present
ev <- ev |> mutate(
  sig = signal_present - 0.5,
  cond = if_else(condition_id == "SYN_NEUTRAL", 0.5, -0.5)
)
m <- glmer(
  yes_response ~ sig * cond + (1 + sig | participant_code),
  family = binomial(link = "probit"), data = ev,
  control = glmerControl(optimizer = "bobyqa",
                         optCtrl = list(maxfun = 2e5))
)
print(round(coef(summary(m)), 2)); print(isSingular(m)); print(VarCorr(m))
