# Exercise 6.2: Produce a sampling manifest and flow report
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

suppressMessages(library(dplyr))
set.seed(62)
listeners <- tibble(
  listener_id = sprintf("SYN_L%02d", 1:60),
  list_id = rep(paste0("L", 1:4), each = 15)
)
items <- tibble(
  item_id = sprintf("I%02d", 1:48),
  talker_id = paste0("T", rep(1:6, times = 8))
)
# simulated withdrawal after session 1
leavers <- sample(listeners$listener_id, 5)
manifest <- listeners |>
  tidyr::crossing(session = 1:2, items) |>
  mutate(withdrew = listener_id %in% leavers & session == 2,
         device_fail = runif(n()) < 0.01, no_response = runif(n()) < 0.02,
         low_quality = runif(n()) < 0.03,
         status = case_when(
           withdrew ~ "withdrawal",
           device_fail ~ "device_failure",
           no_response ~ "missing_response",
           low_quality ~ "acoustic_quality",
           TRUE ~ "analyzed"))
print(count(manifest, status))
