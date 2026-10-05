# Exercise 2.1: Convert topics into discriminating questions
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(tidyverse)
pred <- tribble(
  ~outcome, ~account_A_predicts, ~account_B_predicts, ~manipulation_check,
  "contrast cue", "longer closure in condition X", "no closure difference",
    "condition X words are longer overall than condition Y words",
  "uninformative", "difference near zero, wide interval", "difference near zero, wide interval", "")
write_tsv(pred, "prediction_table.tsv")
