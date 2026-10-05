# Exercise 2.2: Design a replication decision memo
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# --- Part 1 of 3 ---
library(lme4)
sim_data <- function(n_spk = 30, n_item = 20, effect = 10) {
  d <- expand.grid(
    spk = factor(1:n_spk), item = factor(1:n_item), cond = c(0, 1)
  )
  d$y <- 100 + rnorm(n_spk, 0, 12)[d$spk] +
    rnorm(n_item, 0, 8)[d$item] +
    (effect + rnorm(n_spk, 0, 5)[d$spk]) * d$cond +
    rnorm(nrow(d), 0, 20)
  d
}

# --- Part 2 of 3 ---
sesoi <- 5   # smallest effect of interest, in ms
sim_once <- function(...) {
  d <- sim_data(...); odd <- FALSE
  m <- withCallingHandlers(
    tryCatch(
      suppressMessages(
        lmer(y ~ cond + (1 + cond | spk) + (1 | item),
             data = d)
      ),
      error = function(e) NULL
    ),
    warning = function(w) { odd <<- TRUE; invokeRestart("muffleWarning") })
  if (is.null(m)) return(c(hit = NA, odd = 1))
  est <- coef(summary(m))["cond", ]
  c(hit = as.numeric(est[["Estimate"]] -
                       1.96 * est[["Std. Error"]] > sesoi),
    odd = as.numeric(odd || isSingular(m)))
}

# --- Part 3 of 3 ---
set.seed(1); nsim <- 200
out <- replicate(nsim, sim_once())
n_ok <- sum(!is.na(out["hit", ])); n_hit <- sum(out["hit", ], na.rm = TRUE)
ci <- binom.test(n_hit, n_ok)$conf.int
cat(sprintf("goal met %.3f (95%% CI %.3f-%.3f); anomalous fits %.3f; %d of %d fits\n",
            n_hit / n_ok, ci[1], ci[2], mean(out["odd", ]), n_ok, nsim))
