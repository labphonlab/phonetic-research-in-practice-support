script_argument <- sub("^--file=", "", commandArgs(trailingOnly = FALSE)[grep("--file=", commandArgs(trailingOnly = FALSE))])
repository_root <- normalizePath(file.path(dirname(script_argument), "..", ".."), mustWork = TRUE)
source(file.path(repository_root, "companion", "r", "ch09.R"))
data_root <- file.path(repository_root, "companion", "data", "ch09", "synthetic_annotation")

global_manifest <- read_tsv_ch09(file.path(repository_root, "companion", "data", "MANIFEST.tsv"))
chapter_manifest <- global_manifest[grepl("^CH09_", global_manifest$artifact_id), , drop = FALSE]
stopifnot(nrow(chapter_manifest) == 5)
stopifnot(all(chapter_manifest$data_status == "SYNTHETIC_TEACHING_FIXTURE"))
stopifnot(all(chapter_manifest$contains_human_data == "false"))
observed_hashes <- vapply(chapter_manifest$relative_path, function(path) sha256_ch09(file.path(repository_root, "companion", "data", path)), character(1))
stopifnot(all(tolower(observed_hashes) == tolower(chapter_manifest$sha256)))

categorical_output <- tempfile("ch09-categorical-")
categorical <- run_categorical_agreement(file.path(data_root, "annotation_schema.yaml"), file.path(data_root, "annotation_assignments.tsv"), file.path(data_root, "categorical_judgments.tsv"), categorical_output, bootstrap_replicates = 100L)
stopifnot(nrow(categorical$pair) == 120)
stopifnot(is.finite(categorical$agreement$kappa[categorical$agreement$scope == "overall"]))
stopifnot(all(file.exists(file.path(categorical_output, c("categorical_agreement.tsv", "confusion_matrices.tsv", "agreement_diagnostics.html", "analysis_decisions.yaml", "run_provenance.json")))))

boundary_output <- tempfile("ch09-boundary-")
boundary <- run_boundary_and_automation_audit(file.path(data_root, "annotation_schema.yaml"), file.path(data_root, "annotation_assignments.tsv"), file.path(data_root, "boundary_judgments.tsv"), file.path(data_root, "automatic_proposal_audit.tsv"), boundary_output)
stopifnot(nrow(boundary$differences) == 240)
stopifnot(all(c("signed_difference_ms", "absolute_difference_ms", "within_5ms", "within_10ms", "within_20ms") %in% names(boundary$differences)))
stopifnot(nrow(boundary$bias) == 4)
stopifnot(all(file.exists(file.path(boundary_output, c("boundary_differences.tsv", "boundary_diagnostics.html", "automation_bias.tsv", "review_decisions.tsv", "analysis_decisions.yaml", "run_provenance.json")))))

notebooks <- list.files(file.path(repository_root, "companion", "notebooks", "ch09"), pattern = "\\.ipynb$", full.names = TRUE)
stopifnot(length(notebooks) == 2)
for (path in notebooks) {
  payload <- jsonlite::read_json(path, simplifyVector = FALSE)
  stopifnot(payload$nbformat == 4)
  stopifnot(payload$metadata$kernelspec$language == "R")
  stopifnot(grepl("SYNTHETIC_TEACHING_FIXTURE", paste(readLines(path, warn = FALSE), collapse = "\n"), fixed = TRUE))
}
unlink(c(categorical_output, boundary_output), recursive = TRUE, force = TRUE)
cat("PASS companion/tests/test_ch09.R\n")
