script_argument <- sub("^--file=", "", commandArgs(trailingOnly = FALSE)[grep("--file=", commandArgs(trailingOnly = FALSE))])
repository_root <- normalizePath(file.path(dirname(script_argument), "..", ".."), mustWork = TRUE)
source(file.path(repository_root, "companion", "r", "ch11.R"))
data_root <- file.path(repository_root, "companion", "data", "ch11", "synthetic_segmental")

manifest <- read_tsv_ch11(file.path(repository_root, "companion", "data", "MANIFEST.tsv"))
chapter_manifest <- manifest[grepl("^CH11_", manifest$artifact_id), , drop = FALSE]
stopifnot(nrow(chapter_manifest) == 5)
stopifnot(all(chapter_manifest$data_status == "SYNTHETIC_TEACHING_FIXTURE"), all(chapter_manifest$contains_human_data == "false"))
hashes <- vapply(chapter_manifest$relative_path, function(path) sha256_ch11(file.path(repository_root, "companion", "data", path)), character(1))
stopifnot(all(tolower(hashes) == tolower(chapter_manifest$sha256)))

audit_output <- tempfile("ch11-audit-")
audit <- run_segmental_measure_audit(file.path(data_root, "event_dictionary.yaml"), file.path(data_root, "annotation_manifest.tsv"), file.path(data_root, "acoustic_estimates.tsv"), file.path(data_root, "segmental_measure_manifest.tsv"), audit_output)
stopifnot(nrow(audit$raw) == 3240, nrow(audit$audit) > 0)
stopifnot(all(file.exists(file.path(audit_output, c("segmental_raw_measures.tsv", "landmark_audit.tsv", "coverage_by_context.tsv", "segmental_diagnostics.html", "analysis_decisions.yaml", "run_provenance.json")))))

normalization_output <- tempfile("ch11-normalization-")
raw_path <- file.path(audit_output, "segmental_raw_measures.tsv")
raw_hash <- sha256_ch11(raw_path)
normalization <- run_normalization_comparison(raw_path, file.path(data_root, "annotation_manifest.tsv"), file.path(data_root, "split_manifest.tsv"), file.path(data_root, "segmental_measure_manifest.tsv"), normalization_output, bootstrap_replicates = 30L)
stopifnot(normalization$exact_rebuild, normalization$raw_unchanged)
stopifnot(nrow(normalization$parameters) == 90, any(!normalization$parameters$eligible))
stopifnot(raw_hash == sha256_ch11(raw_path))
stopifnot(all(file.exists(file.path(normalization_output, c("normalization_parameters.tsv", "segmental_normalized_measures.tsv", "normalization_stability.tsv", "normalization_diagnostics.html", "normalization_decision.yaml", "run_provenance.json")))))

notebooks <- list.files(file.path(repository_root, "companion", "notebooks", "ch11"), pattern = "\\.ipynb$", full.names = TRUE)
stopifnot(length(notebooks) == 2)
for (path in notebooks) {
  payload <- jsonlite::read_json(path, simplifyVector = FALSE)
  stopifnot(payload$nbformat == 4, payload$metadata$kernelspec$language == "R")
  stopifnot(grepl("SYNTHETIC_TEACHING_FIXTURE", paste(readLines(path, warn = FALSE), collapse = "\n"), fixed = TRUE))
}
unlink(c(audit_output, normalization_output), recursive = TRUE, force = TRUE)
cat("PASS companion/tests/test_ch11.R\n")
