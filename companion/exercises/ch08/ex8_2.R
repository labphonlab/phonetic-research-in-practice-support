# Exercise 8.2: Fit and critique a psychometric function
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# --- Part 1 of 2 ---
suppressMessages({library(readr); library(dplyr); library(lme4)})
d <- read_tsv("companion/data/ch08/synthetic_perception/psychometric_responses.tsv", show_col_types = FALSE) |>
  mutate(step_c = continuum_step - mean(continuum_step))     # centered step
fit <- glmer(
  binary_response ~ step_c + (1 + step_c | participant_code),
  family = binomial, data = d,
  control = glmerControl(optimizer = "bobyqa",
                         optCtrl = list(maxfun = 2e5))
)
b <- fixef(fit); V <- vcov(fit)
g <- c(-1 / b[2], b[1] / b[2]^2)                             # delta-method gradient of -b1/b2
# step at P(B) = .5, zero-random-effect participant
loc <- -b[1] / b[2] + mean(d$continuum_step)
cat(sprintf("slope %.2f (SE %.2f); location %.2f steps (SE %.2f); singular: %s\n",
            b[2], sqrt(V[2, 2]), loc, sqrt(drop(t(g) %*% V %*% g)), isSingular(fit)))
# read the correlation, not only isSingular()
print(VarCorr(fit))
cf <- coef(fit)$participant_code                             # per-participant intercept and slope
print(round(data.frame(slope = cf$step_c, boundary = -cf[[1]] / cf$step_c + mean(d$continuum_step)), 2))

# --- Part 2 of 2 ---
suppressMessages({library(readr); library(dplyr)})
d <- read_tsv("companion/data/ch08/synthetic_perception/psychometric_responses.tsv", show_col_types = FALSE)
nll <- function(p, dat, lapse) {                      # p = intercept, slope, logit lapse rate
  gam <- if (lapse) plogis(p[3]) else 0
  pr <- gam +
    (1 - 2 * gam) * plogis(p[1] + p[2] * dat$continuum_step)
  -sum(dbinom(dat$binary_response, 1, pr, log = TRUE))
}
for (sub in list(-3:3, -2:2)) for (lapse in c(FALSE, TRUE)) {
  dat <- filter(d, continuum_step %in% sub)
  o <- optim(c(0, 1, -3), nll, dat = dat, lapse = lapse)
  cat(sprintf(
    "steps %d to %d, lapse %-5s: slope %.2f, location %.2f\n",
    min(sub), max(sub), lapse, o$par[2], -o$par[1] / o$par[2]
  ))
}
