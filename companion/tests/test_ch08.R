script_argument <- sub("^--file=", "", commandArgs(trailingOnly = FALSE)[grep("--file=", commandArgs(trailingOnly = FALSE))])
repository_root <- normalizePath(file.path(dirname(script_argument), "..", ".."), mustWork = TRUE)
source(file.path(repository_root, "companion", "r", "ch08.R"))

data_root <- file.path(repository_root, "companion", "data", "ch08", "synthetic_perception")
global_manifest <- read_tsv(file.path(repository_root, "companion", "data", "MANIFEST.tsv"))
chapter_manifest <- global_manifest[grepl("^CH08_", global_manifest$artifact_id), , drop = FALSE]
stopifnot(nrow(chapter_manifest) == 13)
stopifnot(all(chapter_manifest$data_status == "SYNTHETIC_TEACHING_FIXTURE"))
stopifnot(all(chapter_manifest$contains_human_data == "false"))
observed_hashes <- vapply(
  chapter_manifest$relative_path,
  function(path) sha256_file(file.path(repository_root, "companion", "data", path)),
  character(1)
)
stopifnot(all(tolower(observed_hashes) == tolower(chapter_manifest$sha256)))

psychometric_output <- tempfile("ch08-psychometric-")
result_psychometric <- run_psychometric_analysis(
  file.path(data_root, "perception_trial_manifest.tsv"),
  file.path(data_root, "stimulus_manifest.tsv"),
  file.path(data_root, "psychometric_responses.tsv"),
  psychometric_output
)
stopifnot(nrow(result_psychometric$parameters) == 13)
stopifnot(any(grepl("nonmonotonic_or_reverse", result_psychometric$parameters$diagnostic_flag)))
stopifnot(all(file.exists(file.path(psychometric_output, c(
  "psychometric_parameters.tsv", "psychometric_diagnostics.html", "analysis_decisions.yaml", "run_provenance.json"
)))))

signal_output <- tempfile("ch08-signal-")
result_signal <- run_signal_detection_analysis(
  file.path(data_root, "detection_event_log.tsv"),
  file.path(data_root, "signal_detection_decisions.yaml"),
  file.path(data_root, "online_timing_audit.tsv"),
  signal_output
)
stopifnot(nrow(result_signal$summary) == 2)
stopifnot(nrow(result_signal$excluded) == 48)
stopifnot(max(result_signal$summary$accuracy) - min(result_signal$summary$accuracy) < 0.10)
stopifnot(max(result_signal$summary$criterion_c) - min(result_signal$summary$criterion_c) > 0.50)
stopifnot(all(file.exists(file.path(signal_output, c(
  "signal_detection_summary.tsv", "reaction_time_diagnostics.html", "excluded_events.tsv",
  "online_experiment_audit.tsv", "analysis_decisions.yaml", "run_provenance.json"
)))))

notebook_root <- file.path(repository_root, "companion", "notebooks", "ch08")
notebooks <- list.files(notebook_root, pattern = "\\.ipynb$", full.names = TRUE)
stopifnot(length(notebooks) == 2)
for (path in notebooks) {
  payload <- jsonlite::read_json(path, simplifyVector = FALSE)
  stopifnot(payload$nbformat == 4)
  stopifnot(payload$metadata$kernelspec$language == "R")
  stopifnot(grepl("SYNTHETIC_TEACHING_FIXTURE", paste(readLines(path, warn = FALSE), collapse = "\n"), fixed = TRUE))
}

unlink(c(psychometric_output, signal_output), recursive = TRUE, force = TRUE)
cat("PASS companion/tests/test_ch08.R\n")
