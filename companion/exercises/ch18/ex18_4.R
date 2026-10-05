# Exercise 18.4: Redesign predictive validation
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# --- Part 1 of 2 ---
library(readr)
p <- read_tsv(
  "companion/data/ch18/synthetic_complex/prediction_features.tsv",
  show_col_types = FALSE
)
cv <- function(p, fold, vars) {
  # centering and scaling are fitted on training rows only
  pr <- rep(NA_real_, nrow(p))
  for (k in sort(unique(fold))) {
    tr <- p[fold != k, ]
    te <- p[fold == k, ]
    mu <- colMeans(tr[vars])
    sdv <- sapply(tr[vars], sd)
    m <- glm(
      tr$outcome ~ .,
      data = as.data.frame(scale(tr[vars], mu, sdv)),
      family = binomial
    )
    pr[fold == k] <- predict(
      m,
      as.data.frame(scale(te[vars], mu, sdv)),
      type = "response"
    )
  }
  pr
}
metrics <- function(y, pr) {
  lp <- qlogis(pmin(pmax(pr, 1e-6), 1 - 1e-6))
  cal <- coef(glm(y ~ lp, family = binomial))
  c(
    accuracy = mean((pr > .5) == y),
    brier = mean((pr - y)^2),
    cal_int = unname(cal[1]),
    cal_slope = unname(cal[2])
  )
}

# --- Part 2 of 2 ---
set.seed(18042026)
spk <- unique(p$speaker_id)
folds <- list(
  row_random = sample(rep(1:5, length.out = nrow(p))),
  speaker_heldout = setNames(
    sample(rep(1:5, length.out = length(spk))),
    spk
  )[p$speaker_id]
)
for (sch in names(folds)) {
  pr <- cv(p, folds[[sch]], c("cue_1", "cue_2"))
  cat(sch, round(metrics(p$outcome, pr), 3), "\n")
}
# speaker-level bootstrap of the last scheme run (speaker_heldout)
acc <- replicate(500, {
  i <- unlist(lapply(
    sample(spk, replace = TRUE),
    function(s) which(p$speaker_id == s)
  ))
  mean((pr[i] > .5) == p$outcome[i])
})
quantile(acc, c(.025, .975))
rep_acc <- replicate(100, {
  fo <- setNames(
    sample(rep(1:5, length.out = length(spk))),
    spk
  )[p$speaker_id]
  # 100 repeated speaker-held-out splits
  metrics(
    p$outcome, cv(p, fo, c("cue_1", "cue_2"))
  )["accuracy"]
})
round(c(mean = mean(rep_acc), quantile(rep_acc, c(.025, .975))), 3)
