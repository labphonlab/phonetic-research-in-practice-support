# Exercise 6.1: Build a multidimensional sampling plan
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# assumed SDs, not estimates
sd_spk <- 0.30; sd_item <- 0.20; sd_res <- 0.50
se_mean <- function(S, I, reps) {
  sqrt(sd_spk^2 / S + sd_item^2 / I +
         sd_res^2 / (S * I * reps))
}
alloc <- data.frame(speakers = c(10, 40), items = c(40, 10),
                    reps = 1)
alloc$tokens <- alloc$speakers * alloc$items * alloc$reps
alloc$se_speaker_part <- sqrt(sd_spk^2 / alloc$speakers)
alloc$se_item_part <- sqrt(sd_item^2 / alloc$items)
alloc$se_total <- se_mean(alloc$speakers, alloc$items,
                          alloc$reps)
print(round(alloc, 3))
