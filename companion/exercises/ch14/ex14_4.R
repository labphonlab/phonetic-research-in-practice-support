# Exercise 14.4: Calibrate the conclusion
# Phonetic Research in Practice, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

# This exercise continues Exercise 14.3: defines `spec` and `run_all()` from Exercise 14.3.
source("companion/exercises/ch14/ex14_3.R")

extra <- data.frame(configuration_id = "empty_sample", priority = "high", measurement_layer = "primary",
                    eligibility_rule = "quality_ge_200", model = "additive",
                    changes_estimand = FALSE, exploratory = FALSE)
res <- run_all(bind_rows(spec, extra))
res |> filter(status == "ok", !changes_estimand, priority %in% c("primary", "high")) |>
  summarise(n = n(), min = min(estimate), max = max(estimate))   # 4 6.02 7.27
sum(res$status != "ok")                                           # 2
dat |> group_by(group_id) |> summarise(share_unavailable = mean(availability_code != "observed"))
# SYN_A 0.083, SYN_B 0.212
