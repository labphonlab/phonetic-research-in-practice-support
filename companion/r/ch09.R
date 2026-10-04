required_packages_ch09 <- c("digest", "jsonlite", "yaml")
missing_packages_ch09 <- required_packages_ch09[!vapply(required_packages_ch09, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing_packages_ch09) > 0) stop("Missing required R packages: ", paste(missing_packages_ch09, collapse = ", "))

read_tsv_ch09 <- function(path) utils::read.delim(path, sep = "\t", quote = "", stringsAsFactors = FALSE, check.names = FALSE)
write_tsv_ch09 <- function(data, path) {
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  utils::write.table(data, path, sep = "\t", quote = FALSE, row.names = FALSE, na = "")
}
assert_columns_ch09 <- function(data, required, label) {
  missing <- setdiff(required, names(data))
  if (length(missing)) stop(label, " is missing columns: ", paste(missing, collapse = ", "))
}
sha256_ch09 <- function(path) digest::digest(file = path, algo = "sha256", serialize = FALSE)
html_table_ch09 <- function(data) {
  esc <- function(x) {
    x <- gsub("&", "&amp;", as.character(x), fixed = TRUE)
    x <- gsub("<", "&lt;", x, fixed = TRUE)
    gsub(">", "&gt;", x, fixed = TRUE)
  }
  header <- paste0("<th>", esc(names(data)), "</th>", collapse = "")
  body <- apply(data, 1, function(row) paste0("<tr>", paste0("<td>", esc(row), "</td>", collapse = ""), "</tr>"))
  paste0("<table border='1'><thead><tr>", header, "</tr></thead><tbody>", paste(body, collapse = ""), "</tbody></table>")
}
write_provenance_ch09 <- function(path, tool, inputs, decisions) {
  jsonlite::write_json(list(
    tool = tool,
    tool_version = "0.1.0",
    r_version = R.version.string,
    run_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
    input_hashes = stats::setNames(lapply(inputs, sha256_ch09), normalizePath(inputs)),
    decisions = decisions
  ), path, pretty = TRUE, auto_unbox = TRUE)
}

kappa_two_raters <- function(label_a, label_b) {
  levels_all <- sort(unique(c(label_a, label_b)))
  table_ab <- table(factor(label_a, levels_all), factor(label_b, levels_all))
  n <- sum(table_ab)
  observed <- sum(diag(table_ab)) / n
  expected <- sum(rowSums(table_ab) * colSums(table_ab)) / (n ^ 2)
  kappa <- if (expected < 1) (observed - expected) / (1 - expected) else NA_real_
  c(observed = observed, expected = expected, kappa = kappa)
}

run_categorical_agreement <- function(schema_path, assignment_path, judgment_path, output_dir, bootstrap_replicates = 500L, seed = 9092026L) {
  schema <- yaml::read_yaml(schema_path)
  assignments <- read_tsv_ch09(assignment_path)
  judgments <- read_tsv_ch09(judgment_path)
  assert_columns_ch09(assignments, c("item_id", "speaker_id", "assignment_status", "data_status"), "assignment table")
  assert_columns_ch09(judgments, c("item_id", "speaker_id", "annotator_id", "label", "judgment_stage", "adjudicated", "data_status"), "judgment table")
  if (!isTRUE(schema$adjudication$preserve_independent_labels)) stop("Schema must preserve independent labels")
  if (any(tolower(as.character(judgments$adjudicated)) == "true") || any(judgments$judgment_stage != "independent_first_pass")) {
    stop("Agreement requires independent first-pass judgments, not adjudicated labels")
  }
  if (!all(c(assignments$data_status, judgments$data_status) == "SYNTHETIC_TEACHING_FIXTURE")) stop("Bundled annotation fixture must remain explicitly synthetic")
  annotators <- sort(unique(judgments$annotator_id))
  if (length(annotators) != 2) stop("Baseline notebook requires exactly two independent annotators")
  first <- judgments[judgments$annotator_id == annotators[[1]], c("item_id", "speaker_id", "condition", "label")]
  second <- judgments[judgments$annotator_id == annotators[[2]], c("item_id", "speaker_id", "condition", "label")]
  names(first)[names(first) == "label"] <- "label_a"
  names(second)[names(second) == "label"] <- "label_b"
  pair <- merge(first, second[, c("item_id", "label_b")], by = "item_id", all = FALSE)
  if (nrow(pair) * 2 != nrow(judgments)) stop("Independent judgment pairing is incomplete")
  overall <- kappa_two_raters(pair$label_a, pair$label_b)
  set.seed(seed)
  clusters <- unique(pair$speaker_id)
  boot <- replicate(bootstrap_replicates, {
    sampled <- sample(clusters, length(clusters), replace = TRUE)
    resampled <- do.call(rbind, lapply(seq_along(sampled), function(index) {
      block <- pair[pair$speaker_id == sampled[[index]], , drop = FALSE]
      block$bootstrap_cluster <- index
      block
    }))
    kappa_two_raters(resampled$label_a, resampled$label_b)[["kappa"]]
  })
  levels_all <- sort(unique(c(pair$label_a, pair$label_b)))
  category_rows <- do.call(rbind, lapply(levels_all, function(category) {
    both <- sum(pair$label_a == category & pair$label_b == category)
    one <- sum(xor(pair$label_a == category, pair$label_b == category))
    data.frame(scope = "category", category = category, n_items = nrow(pair), percent_agreement = NA_real_, expected_agreement = NA_real_, kappa = NA_real_, ci_low = NA_real_, ci_high = NA_real_, positive_agreement = 2 * both / (2 * both + one), stringsAsFactors = FALSE)
  }))
  agreement <- rbind(
    data.frame(scope = "overall", category = "all", n_items = nrow(pair), percent_agreement = overall[["observed"]], expected_agreement = overall[["expected"]], kappa = overall[["kappa"]], ci_low = unname(stats::quantile(boot, 0.025, na.rm = TRUE)), ci_high = unname(stats::quantile(boot, 0.975, na.rm = TRUE)), positive_agreement = NA_real_, stringsAsFactors = FALSE),
    category_rows
  )
  confusion <- as.data.frame(table(label_a = pair$label_a, label_b = pair$label_b), stringsAsFactors = FALSE)
  names(confusion)[3] <- "count"
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  write_tsv_ch09(agreement, file.path(output_dir, "categorical_agreement.tsv"))
  write_tsv_ch09(confusion, file.path(output_dir, "confusion_matrices.tsv"))
  report <- paste0(
    "<!doctype html><meta charset='utf-8'><title>Categorical agreement diagnostics</title>",
    "<h1>Categorical agreement diagnostics</h1><p><strong>Data status:</strong> SYNTHETIC_TEACHING_FIXTURE. Coefficients describe generated judgments, not trained annotators.</p>",
    "<h2>Agreement and category usability</h2>", html_table_ch09(agreement),
    "<h2>Confusion matrix</h2>", html_table_ch09(confusion),
    "<p>Usability must be decided by category and downstream purpose; no coefficient supplies a universal pass threshold.</p>"
  )
  writeLines(report, file.path(output_dir, "agreement_diagnostics.html"), useBytes = TRUE)
  decisions <- list(schema_version = "0.1", data_status = "SYNTHETIC_TEACHING_FIXTURE", primary_statistic = "Cohen kappa", uncertainty = "speaker-cluster bootstrap", bootstrap_replicates = bootstrap_replicates, seed = seed, independent_stage = "independent_first_pass", interpretive_limit = "agreement does not validate the construct")
  yaml::write_yaml(decisions, file.path(output_dir, "analysis_decisions.yaml"))
  write_provenance_ch09(file.path(output_dir, "run_provenance.json"), "run_categorical_agreement", c(schema_path, assignment_path, judgment_path), decisions)
  list(agreement = agreement, confusion = confusion, pair = pair, decisions = decisions)
}

run_boundary_and_automation_audit <- function(schema_path, assignment_path, boundary_path, automation_path, output_dir) {
  schema <- yaml::read_yaml(schema_path)
  assignments <- read_tsv_ch09(assignment_path)
  boundaries <- read_tsv_ch09(boundary_path)
  automation <- read_tsv_ch09(automation_path)
  assert_columns_ch09(boundaries, c("item_id", "speaker_id", "condition", "boundary_type", "annotator_id", "time_ms", "judgment_stage", "data_status"), "boundary table")
  assert_columns_ch09(automation, c("audit_id", "annotation_mode", "difficulty", "automatic_default_label", "final_label", "automatic_default_boundary_ms", "final_boundary_ms", "annotation_time_s", "confidence", "data_status"), "automation audit")
  if (any(boundaries$judgment_stage != "independent_first_pass")) stop("Boundary audit requires independent first-pass judgments")
  if (!all(c(assignments$data_status, boundaries$data_status, automation$data_status) == "SYNTHETIC_TEACHING_FIXTURE")) stop("Bundled Chapter 9 fixture must remain explicitly synthetic")
  annotators <- sort(unique(boundaries$annotator_id))
  if (length(annotators) != 2) stop("Baseline boundary audit requires exactly two annotators")
  first <- boundaries[boundaries$annotator_id == annotators[[1]], c("item_id", "speaker_id", "condition", "boundary_type", "time_ms")]
  second <- boundaries[boundaries$annotator_id == annotators[[2]], c("item_id", "boundary_type", "time_ms")]
  names(first)[names(first) == "time_ms"] <- "time_a_ms"
  names(second)[names(second) == "time_ms"] <- "time_b_ms"
  differences <- merge(first, second, by = c("item_id", "boundary_type"), all = FALSE)
  differences$signed_difference_ms <- differences$time_b_ms - differences$time_a_ms
  differences$absolute_difference_ms <- abs(differences$signed_difference_ms)
  tolerances <- as.numeric(unlist(schema$reliability$boundary_tolerances_ms))
  for (tolerance in tolerances) differences[[paste0("within_", tolerance, "ms")]] <- differences$absolute_difference_ms <= tolerance
  summary <- do.call(rbind, lapply(split(differences, list(differences$condition, differences$boundary_type), drop = TRUE), function(block) {
    data.frame(condition = block$condition[[1]], boundary_type = block$boundary_type[[1]], n = nrow(block), mean_signed_ms = mean(block$signed_difference_ms), median_absolute_ms = stats::median(block$absolute_difference_ms), p90_absolute_ms = unname(stats::quantile(block$absolute_difference_ms, 0.90)), stringsAsFactors = FALSE)
  }))
  automation$default_match <- automation$automatic_default_label == automation$final_label
  automation$boundary_shift_ms <- automation$final_boundary_ms - automation$automatic_default_boundary_ms
  bias <- do.call(rbind, lapply(split(automation, list(automation$annotation_mode, automation$difficulty), drop = TRUE), function(block) {
    data.frame(annotation_mode = block$annotation_mode[[1]], difficulty = block$difficulty[[1]], n = nrow(block), default_match_rate = mean(block$default_match), mean_boundary_shift_ms = mean(block$boundary_shift_ms), median_annotation_time_s = stats::median(block$annotation_time_s), mean_confidence = mean(block$confidence), stringsAsFactors = FALSE)
  }))
  scratch_match <- mean(automation$default_match[automation$annotation_mode == "from_scratch"])
  correction_match <- mean(automation$default_match[automation$annotation_mode == "correct_default"])
  review <- data.frame(
    decision_id = c("category_anchor", "boundary_interchangeability_15ms", "boundary_interchangeability_100ms", "automation_review_design"),
    diagnostic = c(correction_match - scratch_match, max(summary$p90_absolute_ms), max(summary$p90_absolute_ms), correction_match - scratch_match),
    status = c(ifelse(correction_match - scratch_match > 0.10, "review_required", "no_large_anchor_detected"), ifelse(max(summary$p90_absolute_ms) > 7.5, "not_interchangeable", "potentially_interchangeable"), ifelse(max(summary$p90_absolute_ms) > 50, "not_interchangeable", "potentially_interchangeable"), "counterbalanced_review_recommended"),
    rationale = c("Compare default-match rates under correction and from-scratch modes.", "Boundary error is large relative to a 15 ms contrast.", "Boundary error is evaluated relative to a 100 ms contrast.", "Retain default, correction, final judgment, time, confidence, and difficulty."),
    stringsAsFactors = FALSE
  )
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  write_tsv_ch09(differences, file.path(output_dir, "boundary_differences.tsv"))
  write_tsv_ch09(bias, file.path(output_dir, "automation_bias.tsv"))
  write_tsv_ch09(review, file.path(output_dir, "review_decisions.tsv"))
  report <- paste0(
    "<!doctype html><meta charset='utf-8'><title>Boundary and automation diagnostics</title>",
    "<h1>Boundary and automation diagnostics</h1><p><strong>Data status:</strong> SYNTHETIC_TEACHING_FIXTURE. Continuous differences are retained below and are not replaced by binary tolerance labels.</p>",
    "<h2>Boundary summaries</h2>", html_table_ch09(summary),
    "<h2>Automation-mode summaries</h2>", html_table_ch09(bias),
    "<h2>Review decisions</h2>", html_table_ch09(review)
  )
  writeLines(report, file.path(output_dir, "boundary_diagnostics.html"), useBytes = TRUE)
  decisions <- list(schema_version = "0.1", data_status = "SYNTHETIC_TEACHING_FIXTURE", signed_difference = "annotator B minus annotator A", tolerances_ms = tolerances, continuous_distribution_retained = TRUE, automation_comparison = "counterbalanced mode summaries", interpretive_limit = "synthetic judgments do not estimate a field annotation workforce")
  yaml::write_yaml(decisions, file.path(output_dir, "analysis_decisions.yaml"))
  write_provenance_ch09(file.path(output_dir, "run_provenance.json"), "run_boundary_and_automation_audit", c(schema_path, assignment_path, boundary_path, automation_path), decisions)
  list(differences = differences, summary = summary, bias = bias, review = review, decisions = decisions)
}
