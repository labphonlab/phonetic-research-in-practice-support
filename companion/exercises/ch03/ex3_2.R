# Exercise 3.2: Compare normalization estimands
# Research Methods in Phonetics, companion exercise script (MIT License).
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

# --- Step 4: vowel-space geometry ---
# Convex-hull (shoelace) area of each speaker's three vowel means,
# in raw hertz and after z-scoring F1 and F2 within speaker.
hull_area <- function(x, y) {
  i <- chull(x, y)
  x <- x[i]; y <- y[i]
  abs(sum(x * c(y[-1], y[1]) - c(x[-1], x[1]) * y)) / 2
}
means <- d |>
  group_by(speaker) |>
  mutate(F1_z = (F1 - mean(F1)) / sd(F1)) |>
  group_by(speaker, group, vowel) |>
  summarise(across(c(F1, F2, F1_z, F2_z), mean), .groups = "drop")
areas <- means |>
  group_by(speaker, group) |>
  summarise(raw = hull_area(F2, F1), z = hull_area(F2_z, F1_z),
            .groups = "drop")
print(areas |> group_by(group) |> summarise(across(c(raw, z), mean)))
p <- ggplot(means, aes(F2, F1, colour = group, shape = vowel)) +
  geom_point() + scale_x_reverse() + scale_y_reverse()
ggsave("vowel_means_by_group.png", p, width = 5, height = 4)
