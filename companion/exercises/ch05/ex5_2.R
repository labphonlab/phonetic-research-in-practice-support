# Exercise 5.2: Audit a corpus extraction
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

suppressMessages(library(dplyr))
set.seed(52)
n <- 5000
cand <- tibble(token_id = 1:n, speaker_id = sample(sprintf("S%03d", 1:120), n, TRUE),
               raw_hit = TRUE, deduplicated = runif(n) > 0.04,
               context_eligible = runif(n) > 0.25, signal_available = runif(n) > 0.10,
               measurement_success = runif(n) > 0.08, metadata_complete = runif(n) > 0.05)
steps <- c("raw_hit", "deduplicated", "context_eligible",
           "signal_available", "measurement_success", "metadata_complete")
keep <- rep(TRUE, n)
for (s in steps) {
  keep <- keep & cand[[s]]
  cat(sprintf("%-20s tokens = %4d, speakers = %3d\n", s, sum(keep), n_distinct(cand$speaker_id[keep])))
}
