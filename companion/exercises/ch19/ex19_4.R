# Exercise 19.4: Build a claim-evidence map
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

library(readr); library(dplyr)
D <- "companion/data/ch19/synthetic_claims/"
cl <- read_tsv(paste0(D, "draft_claim_registry.tsv"), show_col_types = FALSE)
ev <- read_tsv(paste0(D, "evidence_inventory.tsv"), show_col_types = FALSE)
st <- setNames(ev$status, ev$domain)
cl |> transmute(claim_id, evidence_level, force,
    new_items_ok = !requires_new_items,
    causal_ok = !requires_causal_identification | st[["causal_identification"]] != "absent",
    external_ok = !requires_external_corpus | st[["corpus_inference"]] == "available") |>
  mutate(verdict = if_else(new_items_ok & causal_ok & external_ok, "keep within stated reach", "revise or remove"))
