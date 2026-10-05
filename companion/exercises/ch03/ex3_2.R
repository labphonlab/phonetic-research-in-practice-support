# Exercise 3.2: Compare normalization estimands
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# --- Part 1 of 3 ---
library(tidyverse)
set.seed(20)
vow <- tibble(vowel = c("i", "a", "u"), F1 = c(300, 750, 320), F2 = c(2300, 1300, 800))
spk <- tibble(
  speaker = factor(1:16),
  group = rep(c("A", "B"), each = 8),
  scale = rnorm(16, rep(c(1, 1.12), each = 8), 0.05)
)
d <- crossing(spk, vow, rep = 1:10) |>
  mutate(F1 = F1 * scale * exp(rnorm(n(), 0, 0.05)),
         F2 = F2 * scale * exp(rnorm(n(), 0, 0.05)))
write_tsv(d, "sim_vowels.tsv")

# --- Part 2 of 3 ---
library(tidyverse)
d <- read_tsv("sim_vowels.tsv", show_col_types = FALSE)
# speakers to distrust or drop
d |> count(speaker, vowel) |> filter(n < 5)
d |>
  group_by(speaker) |>
  summarise(n_vowels = n_distinct(vowel)) |>
  count(n_vowels)

# --- Part 3 of 3 ---
library(tidyverse); library(lmerTest)
d <- read_tsv("sim_vowels.tsv", show_col_types = FALSE) |>
  group_by(speaker) |>
  mutate(F2_z = (F2 - mean(F2)) / sd(F2),
         F2_logmean = log(F2) - mean(log(c(F1, F2)))) |>
  ungroup()
fits <- map(c("F2", "F2_z", "F2_logmean"), \(v) {
  m <- lmer(reformulate("group + (1 | speaker)", v),
            data = filter(d, vowel == "i"))
  tibble(measure = v, est = fixef(m)["groupB"],
         se = coef(summary(m))["groupB", "Std. Error"])
})
print(bind_rows(fits))
