script_argument <- sub("^--file=", "", commandArgs(trailingOnly = FALSE)[grep("--file=", commandArgs(trailingOnly = FALSE))])
repository_root <- normalizePath(file.path(dirname(script_argument), "..", ".."), mustWork = TRUE)
source(file.path(repository_root, "companion", "r", "ch12.R"))
data_root <- file.path(repository_root, "companion", "data", "ch12", "synthetic_prosody")

manifest <- read_tsv_ch12(file.path(repository_root, "companion", "data", "MANIFEST.tsv"))
chapter_manifest <- manifest[grepl("^CH12_", manifest$artifact_id), , drop = FALSE]
stopifnot(nrow(chapter_manifest) == 7)
stopifnot(all(chapter_manifest$data_status == "SYNTHETIC_TEACHING_FIXTURE"), all(chapter_manifest$contains_human_data == "false"))
hashes <- vapply(chapter_manifest$relative_path, function(path) sha256_ch12(file.path(repository_root, "companion", "data", path)), character(1))
stopifnot(all(tolower(hashes) == tolower(chapter_manifest$sha256)))

preparation_output <- tempfile("ch12-preparation-")
preparation <- run_pitch_trajectory_preparation(file.path(data_root, "source_manifest.tsv"), file.path(data_root, "interval_manifest.tsv"), file.path(data_root, "landmarks.tsv"), file.path(data_root, "raw_frame_estimates.tsv"), file.path(data_root, "prosodic_trajectory_spec.yaml"), preparation_output)
stopifnot(nrow(preparation$prepared) > 3000, preparation$raw_unchanged)
stopifnot(any(preparation$prepared$value_origin == "interpolated_estimator_failure"))
stopifnot(all(c("structural_unvoiced", "estimator_failure", "quality_rejection", "source_failure") %in% preparation$prepared$gap_code))

model_output <- tempfile("ch12-model-")
model <- run_dynamic_models_and_rhythm(file.path(preparation_output, "trajectory_preprocessing.tsv"), file.path(data_root, "segmented_intervals.tsv"), file.path(data_root, "model_comparison.yaml"), model_output)
stopifnot(nrow(model$predictions) == 204, nrow(model$residual_dependence) == 2)
stopifnot(nrow(model$warnings) >= 1, all(model$warnings$retained_for_review))
stopifnot(!model$gate$frame_count_is_replication_count, !model$gate$typological_classification_permitted)
stopifnot(all(file.exists(file.path(model_output, c("dynamic_model_diagnostics.html", "trajectory_predictions.tsv", "residual_dependence.tsv", "rhythm_metrics_by_unit.tsv", "rhythm_sensitivity.tsv", "model_warnings.tsv", "trajectory_gate.yaml", "run_provenance.json")))))

notebooks <- list.files(file.path(repository_root, "companion", "notebooks", "ch12"), pattern = "\\.ipynb$", full.names = TRUE)
stopifnot(length(notebooks) == 2)
for (path in notebooks) {
  payload <- jsonlite::read_json(path, simplifyVector = FALSE)
  stopifnot(payload$nbformat == 4, payload$metadata$kernelspec$language == "R")
  stopifnot(grepl("SYNTHETIC_TEACHING_FIXTURE", paste(readLines(path, warn = FALSE), collapse = "\n"), fixed = TRUE))
}
unlink(c(preparation_output, model_output), recursive = TRUE, force = TRUE)
cat("PASS companion/tests/test_ch12.R\n")
