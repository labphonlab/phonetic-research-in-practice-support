# Exercise 14.2: Propagate boundary alternatives
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(readr); library(dplyr); library(lmerTest)
d <- "companion/data/ch14/synthetic_error/"
raw <- read_tsv(paste0(d, "raw_analysis_data.tsv"), show_col_types = FALSE) |>
  mutate(dur_ref = offset_reference_ms - onset_reference_ms,
         dur_auto = offset_automatic_ms - onset_automatic_ms,
         onset_shift = onset_automatic_ms - onset_reference_ms)
c(mean(raw$onset_shift), sd(raw$onset_shift), sd(raw$dur_auto - raw$dur_ref))  # 5.09 4.52 2.77
rep <- read_tsv(paste0(d, "repeated_measurements.tsv"), show_col_types = FALSE) |>
  left_join(distinct(raw, observation_id, item_id, group_id), by = "observation_id") |>
  mutate(duration = offset_ms - onset_ms)
fit <- function(f, dat) {
  m <- lmer(f, data = dat, control = lmerControl(optimizer = "bobyqa"))
  c(coef(summary(m))["group_idSYN_B", c("Estimate", "Std. Error")], singular = isSingular(m))
}
f1 <- dur_ref ~ group_id + (1 | speaker_id) + (1 | item_id)
fit(f1, raw); fit(update(f1, dur_auto ~ .), raw)  # -0.83 (0.64); -0.58 (0.68); both singular
f2 <- duration ~ group_id + annotator_id + (1 | speaker_id) + (1 | observation_id)
fit(f2, rep)                                       # -0.60 (1.53), singular
print(VarCorr(lmer(f2, data = rep)), comp = "Std.Dev.")  # speaker SD about 0
