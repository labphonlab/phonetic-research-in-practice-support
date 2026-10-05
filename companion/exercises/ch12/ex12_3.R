# Exercise 12.3: Diagnose a dynamic model
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# This exercise continues Exercise 12.2: builds `fr`, the trajectory table from Exercise 12.2.
source("companion/exercises/ch12/ex12_2.R")

suppressMessages({library(readr); library(dplyr); library(mgcv); library(itsadug)})
# fr: the table from Exercise 12.2, with factors cond, spk, item and t_prop (0-1)
fr <- fr |> arrange(token_id, frame_index) |>
  mutate(cond = factor(condition_id), spk = factor(speaker_id), item = factor(item_id))
fr$series_start <- c(TRUE, fr$token_id[-1] != fr$token_id[-nrow(fr)])
m0 <- bam(st ~ cond + s(t_prop, by = cond, k = 10),
          data = fr, method = "fREML")
# lag-1 residual correlation of the naive model
rho_hat <- acf(resid(m0), plot = FALSE)$acf[2]
f1 <- function(r) bam(
  st ~ cond + s(t_prop, by = cond, k = 10) +
    s(t_prop, spk, bs = "fs", m = 1, k = 6) +
    s(item, bs = "re"),
  data = fr, method = "fREML", rho = r,
  AR.start = fr$series_start
)
m1 <- f1(rho_hat); m1_06 <- f1(0.6)
lag1 <- function(m) acf(resid_gam(m, incl_na = FALSE), plot = FALSE)$acf[2]
round(c(rho_hat = rho_hat, estimated = lag1(m1),
        prespecified = lag1(m1_06)), 2)
round(summary(m0)$p.table, 2)
round(summary(m1)$p.table, 2)
round(summary(m1_06)$p.table, 2)
