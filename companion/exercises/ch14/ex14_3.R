# Exercise 14.3: Design a bounded sensitivity universe
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# --- Part 1 of 2 ---
library(readr); library(dplyr); library(lmerTest)
d <- "companion/data/ch14/synthetic_error/"
dat <- read_tsv(paste0(d, "raw_analysis_data.tsv"), show_col_types = FALSE) |>
  mutate(
    outcome_bias_corrected =
      outcome_primary - if_else(group_id == "SYN_B", 4, 0)
  )
spec <- read_tsv(paste0(d, "specification_table.tsv"),
                 show_col_types = FALSE)
y_of <- c(primary = "outcome_primary",
          reference = "outcome_true",
          bias_corrected = "outcome_bias_corrected")
x_of <- c(primary = "predictor_primary",
          reference = "predictor_true",
          bias_corrected = "predictor_primary")
rules <- list(
  observed = dat$availability_code == "observed",
  all = rep(TRUE, nrow(dat)),
  quality_ge_050 = dat$quality_score >= 0.5,
  quality_ge_075 = dat$quality_score >= 0.75,
  quality_ge_200 = dat$quality_score >= 2
)

# --- Part 2 of 2 ---
run <- function(s) {
  tryCatch({
    z <- dat[rules[[s$eligibility_rule]] &
               !is.na(dat[[y_of[[s$measurement_layer]]]]), ]
    z$y <- z[[y_of[[s$measurement_layer]]]]
    z$x <- z[[x_of[[s$measurement_layer]]]]
    rhs <- if (s$model == "interaction") "x * group_id" else "x + group_id"
    cf <- coef(summary(lmer(
      as.formula(paste("y ~", rhs, "+ (1 | speaker_id)")),
      data = z)))["x", ]
    data.frame(configuration_id = s$configuration_id,
               estimate = cf[["Estimate"]], se = cf[["Std. Error"]],
               n_obs = nrow(z), n_speakers = n_distinct(z$speaker_id),
               status = "ok")
  }, error = function(e) data.frame(configuration_id = s$configuration_id,
      status = paste("failed:", conditionMessage(e))))
}
run_all <- function(spec)
  bind_rows(lapply(
    split(spec, spec$configuration_id)[spec$configuration_id], run
  )) |>
  left_join(spec, by = "configuration_id")
res <- run_all(spec)
write_tsv(res, "specification_results.tsv")
