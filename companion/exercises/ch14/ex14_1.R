# Exercise 14.1: Construct an error map
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(readr); library(dplyr); library(irr)
d <- "companion/data/ch14/synthetic_error/"
vp <- read_tsv(paste0(d, "validation_pairs.tsv"), show_col_types = FALSE) |>
  filter(validation_status == "paired")
i <- icc(vp[, c("reference_outcome", "measured_outcome")],
         # ICC(2,1)
         model = "twoway", type = "agreement",
         unit = "single")
# 0.879 0.756 0.933
round(c(i$value, i$lbound, i$ubound), 3)
vp |> group_by(group_id) |>
  summarise(n = n(),
            bias = mean(measured_outcome - reference_outcome))
# SYN_A: bias 0.39 (n = 57); SYN_B: bias 4.06 (n = 46)
