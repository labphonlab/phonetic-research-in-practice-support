required_packages_ch14 <- c("digest", "jsonlite", "yaml")
missing_packages_ch14 <- required_packages_ch14[!vapply(required_packages_ch14, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing_packages_ch14)) stop("Missing R packages: ", paste(missing_packages_ch14, collapse = ", "))

read_tsv_ch14 <- function(path) utils::read.delim(path, sep = "\t", quote = "", stringsAsFactors = FALSE, check.names = FALSE)
write_tsv_ch14 <- function(data, path) { dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE); utils::write.table(data, path, sep = "\t", quote = FALSE, row.names = FALSE, na = "") }
sha256_ch14 <- function(path) digest::digest(file = path, algo = "sha256", serialize = FALSE)
html_table_ch14 <- function(data) {
  esc <- function(x) { x <- gsub("&", "&amp;", as.character(x), fixed = TRUE); x <- gsub("<", "&lt;", x, fixed = TRUE); gsub(">", "&gt;", x, fixed = TRUE) }
  paste0("<table border='1'><thead><tr>", paste0("<th>", esc(names(data)), "</th>", collapse = ""), "</tr></thead><tbody>", paste(apply(data, 1, function(row) paste0("<tr>", paste0("<td>", esc(row), "</td>", collapse = ""), "</tr>")), collapse = ""), "</tbody></table>")
}
write_provenance_ch14 <- function(path, tool, inputs, decisions) jsonlite::write_json(list(tool = tool, tool_version = "0.1.0", r_version = R.version.string, run_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE), input_hashes = stats::setNames(lapply(inputs, sha256_ch14), normalizePath(inputs)), decisions = decisions), path, pretty = TRUE, auto_unbox = TRUE)

fit_slope_ch14 <- function(outcome, predictor, group, speaker) {
  keep <- is.finite(outcome) & is.finite(predictor)
  model <- stats::lm(outcome[keep] ~ predictor[keep] + factor(group[keep]))
  summary_row <- summary(model)$coefficients[2, ]
  c(estimate = unname(summary_row[1]), standard_error = unname(summary_row[2]), n = sum(keep), speakers = length(unique(speaker[keep])))
}

run_error_propagation <- function(spec_path, error_map_path, validation_path, repeated_path, raw_path, output_dir) {
  specification <- yaml::read_yaml(spec_path)
  error_map <- read_tsv_ch14(error_map_path); validation <- read_tsv_ch14(validation_path); repeated <- read_tsv_ch14(repeated_path); raw <- read_tsv_ch14(raw_path)
  if (!all(c(error_map$data_status, validation$data_status, repeated$data_status, raw$data_status) == "SYNTHETIC_TEACHING_FIXTURE")) stop("Bundled Chapter 14 inputs must remain explicitly synthetic")
  raw_hash <- sha256_ch14(raw_path)
  raw$predictor_primary <- as.numeric(raw$predictor_primary); raw$outcome_primary <- as.numeric(raw$outcome_primary)
  base <- fit_slope_ch14(raw$outcome_primary, raw$predictor_primary, raw$group_id, raw$speaker_id)
  validation$predictor_error <- as.numeric(validation$measured_predictor) - as.numeric(validation$reference_predictor)
  validation$outcome_error <- as.numeric(validation$measured_outcome) - as.numeric(validation$reference_outcome)
  predictor_sd <- stats::sd(validation$predictor_error, na.rm = TRUE); outcome_sd <- stats::sd(validation$outcome_error, na.rm = TRUE)
  repeat_wide_on <- reshape(repeated[, c("observation_id", "annotator_id", "onset_ms")], idvar = "observation_id", timevar = "annotator_id", direction = "wide")
  repeat_wide_off <- reshape(repeated[, c("observation_id", "annotator_id", "offset_ms")], idvar = "observation_id", timevar = "annotator_id", direction = "wide")
  onset_diff <- repeat_wide_on[[3]] - repeat_wide_on[[2]]; offset_diff <- repeat_wide_off[[3]] - repeat_wide_off[[2]]
  components <- data.frame(error_map, observed_or_declared_scale = c(outcome_sd, predictor_sd, stats::sd(onset_diff), 2.2, 4.0, mean(raw$availability_code != "observed")), scale_unit = c("outcome units", "predictor units", "ms paired onset difference", "outcome units per speaker", "outcome units in SYN_B", "failure proportion"), evidence_status = c("observed_validation", "observed_validation", "observed_repeatability", "generator_known_hypothetical", "generator_known_hypothetical", "observed_fixture"), stringsAsFactors = FALSE)
  set.seed(as.integer(specification$seed))
  mechanisms <- c("outcome_random", "predictor_random", "landmark_shared", "speaker_reference", "differential_group", "differential_missingness")
  manifest_rows <- list(); effect_rows <- list(); index <- 0
  for (mechanism in mechanisms) for (replicate_id in seq_len(as.integer(specification$propagation$replicates))) {
    index <- index + 1; data <- raw; outcome <- data$outcome_primary; predictor <- data$predictor_primary
    estimand <- "additive_predictor_slope"
    if (mechanism == "outcome_random") outcome <- outcome + stats::rnorm(nrow(data), 0, outcome_sd)
    if (mechanism == "predictor_random") predictor <- predictor + stats::rnorm(nrow(data), 0, predictor_sd)
    if (mechanism == "speaker_reference") { shifts <- stats::setNames(stats::rnorm(length(unique(data$speaker_id)), 0, 2.2), unique(data$speaker_id)); outcome <- outcome + shifts[data$speaker_id] }
    if (mechanism == "differential_group") outcome <- outcome - ifelse(data$group_id == "SYN_B", stats::runif(1, 0, 4), 0)
    if (mechanism == "differential_missingness") outcome[data$group_id == "SYN_B" & stats::runif(nrow(data)) < 0.12] <- NA_real_
    if (mechanism == "landmark_shared") {
      estimand <- "landmark_alignment_minus_duration_error"
      shared <- stats::rnorm(nrow(data), mean(onset_diff, na.rm = TRUE), stats::sd(onset_diff, na.rm = TRUE))
      independent <- stats::rnorm(nrow(data), 0, stats::sd(offset_diff - onset_diff, na.rm = TRUE))
      estimate <- mean(abs(shared), na.rm = TRUE) - mean(abs(independent), na.rm = TRUE); se <- stats::sd(abs(shared) - abs(independent), na.rm = TRUE) / sqrt(nrow(data)); n <- nrow(data)
    } else { fit <- fit_slope_ch14(outcome, predictor, data$group_id, data$speaker_id); estimate <- fit[["estimate"]]; se <- fit[["standard_error"]]; n <- fit[["n"]] }
    dataset_id <- sprintf("%s_%03d", mechanism, replicate_id)
    dataset_hash <- digest::digest(list(outcome = outcome, predictor = predictor), algo = "sha256")
    manifest_rows[[index]] <- data.frame(dataset_id = dataset_id, mechanism = mechanism, replicate_id = replicate_id, seed = as.integer(specification$seed), dependency_level = ifelse(mechanism == "speaker_reference", "speaker", ifelse(mechanism == "differential_group", "group", "observation")), row_count = nrow(data), dataset_hash = dataset_hash, data_status = "SYNTHETIC_TEACHING_FIXTURE")
    effect_rows[[index]] <- data.frame(dataset_id = dataset_id, mechanism = mechanism, estimand = estimand, estimate = estimate, standard_error = se, n = n, primary_estimate = base[["estimate"]], data_status = "SYNTHETIC_TEACHING_FIXTURE")
  }
  manifest <- do.call(rbind, manifest_rows); effects <- do.call(rbind, effect_rows)
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  write_tsv_ch14(components, file.path(output_dir, "error_components.tsv")); write_tsv_ch14(manifest, file.path(output_dir, "propagated_datasets_manifest.tsv")); write_tsv_ch14(effects, file.path(output_dir, "measurement_effects.tsv"))
  report <- paste0("<!doctype html><meta charset='utf-8'><title>Error propagation</title><h1>Error propagation</h1><p><strong>Data status:</strong> SYNTHETIC_TEACHING_FIXTURE. Observed fixture diagnostics and generator-known hypothetical ranges are labeled separately.</p>", html_table_ch14(components))
  writeLines(report, file.path(output_dir, "error_diagnostics.html"), useBytes = TRUE)
  if (raw_hash != sha256_ch14(raw_path)) stop("Raw analysis data changed")
  write_provenance_ch14(file.path(output_dir, "run_provenance.json"), "run_error_propagation", c(spec_path, error_map_path, validation_path, repeated_path, raw_path), list(primary = base, raw_unchanged = TRUE, replicates = specification$propagation$replicates))
  list(components = components, manifest = manifest, effects = effects, primary = base, raw_unchanged = TRUE)
}

run_sensitivity_universe <- function(raw_path, config_path, spec_path, output_dir) {
  raw <- read_tsv_ch14(raw_path); configurations <- read_tsv_ch14(config_path); specification <- yaml::read_yaml(spec_path)
  if (!all(c(raw$data_status) == "SYNTHETIC_TEACHING_FIXTURE")) stop("Bundled Chapter 14 sensitivity data must remain explicitly synthetic")
  if (configurations$configuration_id[[1]] != specification$primary_analysis$configuration_id) stop("Primary configuration must run first")
  results <- list(); failures <- list(); result_index <- 0; failure_index <- 0
  for (i in seq_len(nrow(configurations))) {
    config <- configurations[i, ]; data <- raw
    if (config$measurement_layer == "primary") { data$x <- as.numeric(data$predictor_primary); data$y <- as.numeric(data$outcome_primary) }
    else if (config$measurement_layer == "reference") { data$x <- as.numeric(data$predictor_true); data$y <- as.numeric(data$outcome_true) }
    else if (config$measurement_layer == "bias_corrected") { data$x <- as.numeric(data$predictor_primary); data$y <- as.numeric(data$outcome_primary) - ifelse(data$group_id == "SYN_B", 4, 0) }
    else { failure_index <- failure_index + 1; failures[[failure_index]] <- data.frame(configuration_id = config$configuration_id, failure_stage = "measurement_layer", failure_reason = "unknown prespecified measurement layer", retained_in_denominator = TRUE, priority = config$priority, exploratory = config$exploratory, data_status = "SYNTHETIC_TEACHING_FIXTURE"); next }
    if (config$eligibility_rule == "observed") data <- data[is.finite(data$y), ]
    else if (config$eligibility_rule == "quality_ge_050") data <- data[is.finite(data$y) & as.numeric(data$quality_score) >= .50, ]
    else if (config$eligibility_rule == "quality_ge_075") data <- data[is.finite(data$y) & as.numeric(data$quality_score) >= .75, ]
    else if (config$eligibility_rule != "all") stop("Unknown eligibility rule")
    formula <- if (config$model == "interaction") y ~ x * factor(group_id) else y ~ x + factor(group_id)
    fit <- stats::lm(formula, data = data); coefficient <- summary(fit)$coefficients["x", ]
    result_index <- result_index + 1
    results[[result_index]] <- data.frame(configuration_id = config$configuration_id, execution_order = i, priority = config$priority, measurement_layer = config$measurement_layer, eligibility_rule = config$eligibility_rule, model = config$model, changes_estimand = config$changes_estimand, exploratory = config$exploratory, estimand = ifelse(config$model == "interaction", "predictor slope in reference group", "additive predictor slope"), estimate = coefficient[[1]], standard_error = coefficient[[2]], ci_low = coefficient[[1]] - 1.96 * coefficient[[2]], ci_high = coefficient[[1]] + 1.96 * coefficient[[2]], n = nrow(data), speakers = length(unique(data$speaker_id)), groups = length(unique(data$group_id)), diagnostic_status = ifelse(is.finite(coefficient[[1]]) & is.finite(coefficient[[2]]), "pass", "fail"), data_status = "SYNTHETIC_TEACHING_FIXTURE")
  }
  result_table <- do.call(rbind, results); failure_table <- if (length(failures)) do.call(rbind, failures) else data.frame(configuration_id = character(), failure_stage = character(), failure_reason = character(), retained_in_denominator = logical(), priority = character(), exploratory = logical(), data_status = character())
  high <- result_table[result_table$priority %in% c("primary", "high") & result_table$changes_estimand == "false" & result_table$exploratory == "false", ]
  magnitude <- unlist(specification$stability$magnitude_region)
  direction_stable <- all(high$estimate > 0); magnitude_stable <- all(high$estimate >= magnitude[[1]] & high$estimate <= magnitude[[2]]); scope_stable <- all(high$speakers >= 18 & high$groups == 2); diagnostics_stable <- all(high$diagnostic_status == "pass")
  outcome <- if (direction_stable && magnitude_stable && scope_stable && diagnostics_stable) "stable" else if (direction_stable && magnitude_stable && diagnostics_stable) "stable_with_restricted_scope" else if (!magnitude_stable) "measurement_dependent" else "unsupported"
  stability <- data.frame(dimension = c("direction", "magnitude", "scope", "diagnostics", "failed_specifications"), stable = c(direction_stable, magnitude_stable, scope_stable, diagnostics_stable, nrow(failure_table) == 0), evidence = c(paste(range(high$estimate), collapse = " to "), paste0("required ", magnitude[[1]], " to ", magnitude[[2]]), paste(range(high$speakers), collapse = " to "), paste(unique(high$diagnostic_status), collapse = ","), paste(failure_table$configuration_id, collapse = ",")), data_status = "SYNTHETIC_TEACHING_FIXTURE")
  conclusion <- list(data_status = "SYNTHETIC_TEACHING_FIXTURE", primary_configuration = specification$primary_analysis$configuration_id, permitted_claim = "positive association in the generated sample under successful high-priority same-estimand configurations", limitations = c("synthetic results do not quantify empirical measurement uncertainty", "exploratory and changed-estimand branches do not replace the primary result"), result_universe_outcome = outcome)
  gate <- list(data_status = "SYNTHETIC_TEACHING_FIXTURE", decision = outcome, direction_stable = direction_stable, magnitude_stable = magnitude_stable, scope_stable = scope_stable, diagnostics_stable = diagnostics_stable, failed_specifications_retained = nrow(failure_table), significance_vote_permitted = FALSE)
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  write_tsv_ch14(result_table, file.path(output_dir, "specification_results.tsv")); write_tsv_ch14(failure_table, file.path(output_dir, "specification_failures.tsv")); write_tsv_ch14(stability, file.path(output_dir, "claim_stability.tsv"))
  writeLines(paste0("<!doctype html><meta charset='utf-8'><title>Specification universe</title><h1>Specification universe</h1><p><strong>Data status:</strong> SYNTHETIC_TEACHING_FIXTURE. Results are grouped by consequential decisions, not counted as significance votes.</p>", html_table_ch14(result_table)), file.path(output_dir, "specification_curve.html"), useBytes = TRUE)
  yaml::write_yaml(conclusion, file.path(output_dir, "conclusion_map.yaml")); yaml::write_yaml(gate, file.path(output_dir, "claim_stability_gate.yaml"))
  write_provenance_ch14(file.path(output_dir, "run_provenance.json"), "run_sensitivity_universe", c(raw_path, config_path, spec_path), list(gate = gate, execution_order = configurations$configuration_id))
  list(results = result_table, failures = failure_table, stability = stability, conclusion = conclusion, gate = gate)
}
