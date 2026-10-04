required_packages_ch17 <- c("digest", "jsonlite", "nlme", "yaml")
missing_packages_ch17 <- required_packages_ch17[!vapply(required_packages_ch17, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing_packages_ch17)) stop("Missing R packages: ", paste(missing_packages_ch17, collapse = ", "))

STATUS_CH17 <- "SYNTHETIC_TEACHING_FIXTURE"
read_tsv_ch17 <- function(path) utils::read.delim(path, sep = "\t", quote = "", stringsAsFactors = FALSE, check.names = FALSE)
write_tsv_ch17 <- function(data, path) { dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE); utils::write.table(data, path, sep = "\t", quote = FALSE, row.names = FALSE, na = "") }
sha256_ch17 <- function(path) digest::digest(file = path, algo = "sha256", serialize = FALSE)
write_provenance_ch17 <- function(path, tool, inputs, decisions) jsonlite::write_json(list(tool = tool, tool_version = "0.1.0", r_version = R.version.string, run_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE), input_hashes = stats::setNames(lapply(inputs, sha256_ch17), normalizePath(inputs)), decisions = decisions), path, pretty = TRUE, auto_unbox = TRUE)
html_table_ch17 <- function(data) {
  escape <- function(x) { x <- gsub("&", "&amp;", as.character(x), fixed = TRUE); x <- gsub("<", "&lt;", x, fixed = TRUE); gsub(">", "&gt;", x, fixed = TRUE) }
  paste0("<table border='1'><thead><tr>", paste0("<th>", escape(names(data)), "</th>", collapse = ""), "</tr></thead><tbody>", paste(apply(data, 1, function(row) paste0("<tr>", paste0("<td>", escape(row), "</td>", collapse = ""), "</tr>")), collapse = ""), "</tbody></table>")
}
prepare_data_ch17 <- function(data) {
  data$condition <- factor(data$condition, levels = c("BASE", "SHIFT_A", "SHIFT_B"))
  data$speaker_id <- factor(data$speaker_id)
  data$item_id <- factor(data$item_id)
  data$outcome <- as.numeric(data$outcome)
  data$speaking_rate_z <- as.numeric(data$speaking_rate_z)
  data
}
capture_fit_ch17 <- function(expression) {
  warnings <- character(); error <- ""
  fit <- tryCatch(withCallingHandlers(expression, warning = function(w) { warnings <<- c(warnings, conditionMessage(w)); invokeRestart("muffleWarning") }), error = function(e) { error <<- conditionMessage(e); NULL })
  list(fit = fit, warning = paste(unique(warnings), collapse = " | "), error = error)
}
fixed_formula_ch17 <- stats::as.formula("outcome ~ condition + speaking_rate_z + item_id")

fit_candidates_ch17 <- function(data) {
  controls <- nlme::lmeControl(maxIter = 100, msMaxIter = 150, returnObject = TRUE, opt = "optim")
  candidates <- list(
    fixed_only = capture_fit_ch17(stats::lm(fixed_formula_ch17, data = data)),
    speaker_intercept = capture_fit_ch17(nlme::lme(fixed_formula_ch17, random = ~1 | speaker_id, data = data, method = "REML", control = controls)),
    speaker_slope = capture_fit_ch17(nlme::lme(fixed_formula_ch17, random = ~condition | speaker_id, data = data, method = "REML", control = controls))
  )
  candidates
}

write_grouping_graph_ch17 <- function(path) {
  svg <- paste0('<svg xmlns="http://www.w3.org/2000/svg" width="900" height="330">',
    '<style>text{font-family:sans-serif;font-size:14px}.small{font-size:12px}</style>',
    '<rect x="330" y="25" width="240" height="55" rx="8" fill="#e9f2fb" stroke="#345"/><text x="450" y="58" text-anchor="middle">1,296 observations</text>',
    '<line x1="400" y1="80" x2="225" y2="145" stroke="#527a9b"/><line x1="500" y1="80" x2="675" y2="145" stroke="#527a9b"/>',
    '<rect x="105" y="145" width="240" height="55" rx="8" fill="#e8f5e9" stroke="#345"/><text x="225" y="178" text-anchor="middle">24 speakers: random effects</text>',
    '<rect x="555" y="145" width="240" height="55" rx="8" fill="#fff3cd" stroke="#345"/><text x="675" y="178" text-anchor="middle">18 items: fixed blocking effects</text>',
    '<text x="450" y="250" text-anchor="middle">Conceptual design: crossed speakers × items</text>',
    '<text class="small" x="450" y="280" text-anchor="middle">Implementation limit: nlme model does not estimate crossed item random effects here.</text>',
    '<text class="small" x="450" y="305" text-anchor="middle">Therefore new-speaker inference may be considered; new-item inference is prohibited.</text></svg>')
  writeLines(svg, path, useBytes = TRUE)
}

run_estimand_design_and_models <- function(data_path, schema_path, specification_path, contrasts_path, adverse_path, output_dir) {
  data <- read_tsv_ch17(data_path); adverse <- read_tsv_ch17(adverse_path); schema <- yaml::read_yaml(schema_path); specification <- yaml::read_yaml(specification_path); contrast_table <- read_tsv_ch17(contrasts_path)
  if (!all(c(data$data_status, adverse$data_status, specification$data_status) == STATUS_CH17)) stop("Bundled Chapter 17 inputs must remain explicitly synthetic")
  source_hash <- sha256_ch17(data_path); required <- unlist(schema$required_fields); missing_fields <- setdiff(required, names(data)); if (length(missing_fields)) stop("Missing required fields: ", paste(missing_fields, collapse = ", "))
  duplicate_canonical <- duplicated(data$observation_id); duplicate_adverse <- duplicated(adverse$observation_id) | duplicated(adverse$observation_id, fromLast = TRUE)
  support_adverse <- stats::aggregate(observation_id ~ speaker_id + condition, adverse, length)
  adverse_speakers <- unique(adverse$speaker_id); expected_grid <- expand.grid(speaker_id = adverse_speakers, condition = c("BASE", "SHIFT_A", "SHIFT_B"), stringsAsFactors = FALSE)
  support_adverse <- merge(expected_grid, support_adverse, all.x = TRUE); support_adverse$observation_id[is.na(support_adverse$observation_id)] <- 0
  under_supported <- support_adverse$observation_id < as.integer(schema$support_rules$minimum_observations_per_speaker_condition_for_random_slope)
  if (any(duplicate_canonical)) stop("Canonical observation identifiers are not unique")
  data <- prepare_data_ch17(data)
  support <- stats::aggregate(observation_id ~ speaker_id + item_id + condition, data, length)
  names(support)[names(support) == "observation_id"] <- "observations"
  speaker_condition <- stats::aggregate(observation_id ~ speaker_id + condition, data, length); names(speaker_condition)[3] <- "observations"
  item_condition <- stats::aggregate(observation_id ~ item_id + condition, data, length); names(item_condition)[3] <- "observations"
  speaker_condition$support_unit <- "speaker_condition"; item_condition$support_unit <- "item_condition"
  speaker_condition$item_id <- "ALL"; item_condition$speaker_id <- "ALL"
  data_support <- rbind(speaker_condition[, c("support_unit", "speaker_id", "item_id", "condition", "observations")], item_condition[, c("support_unit", "speaker_id", "item_id", "condition", "observations")])
  data_support$data_status <- STATUS_CH17

  design_rows <- list(); index <- 0
  for (coding in unique(contrast_table$coding_id)) {
    mapping <- contrast_table[contrast_table$coding_id == coding, ]
    for (row_index in seq_len(nrow(data))) {
      map_row <- mapping[mapping$condition == as.character(data$condition[[row_index]]), ]
      index <- index + 1
      design_rows[[index]] <- data.frame(observation_id = data$observation_id[[row_index]], coding_id = coding, intercept = 1, condition_column_1 = as.numeric(map_row$column_1), condition_column_2 = as.numeric(map_row$column_2), speaking_rate_z = data$speaking_rate_z[[row_index]], data_status = STATUS_CH17)
    }
  }
  design_matrix <- do.call(rbind, design_rows)
  fits <- fit_candidates_ch17(data)
  attempts <- list(); order <- c("fixed_only", "speaker_intercept", "speaker_slope")
  formulas <- c(fixed_only = "outcome ~ condition + speaking_rate_z + item_id", speaker_intercept = "fixed + (1 | speaker_id)", speaker_slope = "fixed + (condition | speaker_id)")
  simplification_order <- c(speaker_slope = 1, speaker_intercept = 2, fixed_only = 3)
  for (model_id in order) {
    result <- fits[[model_id]]; converged <- !is.null(result$fit) && !nzchar(result$error)
    variance_note <- "not_applicable"
    if (converged && inherits(result$fit, "lme")) {
      variances <- suppressWarnings(as.numeric(nlme::VarCorr(result$fit)[, "Variance"])); variances <- variances[is.finite(variances)]
      variance_note <- ifelse(any(variances < 1e-6), "near_zero_variance_detected", "no_near_zero_variance_detected")
    }
    attempts[[length(attempts) + 1]] <- data.frame(model_id = model_id, attempt_type = "candidate_model", formula = formulas[[model_id]], status = ifelse(converged, "fit", "failed"), warning = result$warning, error = result$error, variance_check = variance_note, inferential_scope = ifelse(model_id == "fixed_only", "observed speakers and observed items", "new speakers conditional on diagnostics; observed items only"), simplification_step = simplification_order[[model_id]], data_status = STATUS_CH17)
  }
  attempts[[length(attempts) + 1]] <- data.frame(model_id = "adverse_duplicate_key", attempt_type = "validation_case", formula = "not_fit", status = ifelse(any(duplicate_adverse), "failed_as_designed", "unexpected_pass"), warning = "", error = paste0("duplicate_rows=", sum(duplicate_adverse)), variance_check = "not_applicable", inferential_scope = "none", simplification_step = NA, data_status = STATUS_CH17)
  attempts[[length(attempts) + 1]] <- data.frame(model_id = "adverse_slope_support", attempt_type = "validation_case", formula = "condition | speaker_id", status = ifelse(any(under_supported), "failed_as_designed", "unexpected_pass"), warning = "", error = paste0("under_supported_cells=", sum(under_supported)), variance_check = "not_applicable", inferential_scope = "none", simplification_step = NA, data_status = STATUS_CH17)
  model_attempts <- do.call(rbind, attempts)
  successful <- order[vapply(fits[order], function(x) !is.null(x$fit) && !nzchar(x$error), logical(1))]
  selected <- if ("speaker_slope" %in% successful) "speaker_slope" else if ("speaker_intercept" %in% successful) "speaker_intercept" else "fixed_only"
  estimand_record <- specification$estimand
  estimand_record$data_status <- STATUS_CH17; estimand_record$outcome_family <- specification$outcome_family; estimand_record$selected_model <- selected
  estimand_record$implementation_limit <- "Items are fixed blocking effects; the fitted model does not support generalization to new items."
  estimand_record$adverse_validation <- list(duplicate_key_detected = any(duplicate_adverse), under_supported_random_slope_detected = any(under_supported))
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  yaml::write_yaml(estimand_record, file.path(output_dir, "estimand_record.yaml")); write_tsv_ch17(design_matrix, file.path(output_dir, "design_matrix.tsv")); write_tsv_ch17(data_support, file.path(output_dir, "data_support.tsv")); write_tsv_ch17(model_attempts, file.path(output_dir, "model_attempts.tsv")); write_grouping_graph_ch17(file.path(output_dir, "grouping_graph.svg"))
  for (model_id in successful) saveRDS(fits[[model_id]]$fit, file.path(output_dir, paste0(model_id, ".rds")))
  if (sha256_ch17(data_path) != source_hash) stop("Canonical analysis data changed")
  decisions <- list(selected_model = selected, successful_models = successful, duplicate_adverse_detected = any(duplicate_adverse), under_supported_slope_detected = any(under_supported), item_scope = "observed_items_only", significance_voting = FALSE, source_unchanged = TRUE)
  write_provenance_ch17(file.path(output_dir, "run_provenance.json"), "run_estimand_design_and_models", c(data_path, schema_path, specification_path, contrasts_path, adverse_path), decisions)
  list(data = data, design_matrix = design_matrix, support = data_support, attempts = model_attempts, fits = fits, selected_model = selected, decisions = decisions)
}

fixed_coefficients_ch17 <- function(model) if (inherits(model, "lme")) nlme::fixed.effects(model) else stats::coef(model)
fixed_vcov_ch17 <- function(model) stats::vcov(model)
model_matrix_ch17 <- function(newdata, coefficient_names) {
  matrix <- stats::model.matrix(stats::delete.response(stats::terms(fixed_formula_ch17)), newdata)
  missing <- setdiff(coefficient_names, colnames(matrix))
  if (length(missing)) matrix <- cbind(matrix, matrix(0, nrow(matrix), length(missing), dimnames = list(NULL, missing)))
  matrix[, coefficient_names, drop = FALSE]
}
average_vector_ch17 <- function(condition, rate, item_levels, coefficient_names) {
  grid <- data.frame(condition = factor(condition, levels = c("BASE", "SHIFT_A", "SHIFT_B")), speaking_rate_z = rate, item_id = factor(item_levels, levels = item_levels))
  colMeans(model_matrix_ch17(grid, coefficient_names))
}
contrast_estimate_ch17 <- function(model, numerator, denominator, item_levels, rate = 0) {
  beta <- fixed_coefficients_ch17(model); covariance <- fixed_vcov_ch17(model); coefficients <- names(beta)
  vector <- average_vector_ch17(numerator, rate, item_levels, coefficients) - average_vector_ch17(denominator, rate, item_levels, coefficients)
  estimate <- sum(vector * beta); standard_error <- sqrt(as.numeric(t(vector) %*% covariance[coefficients, coefficients, drop = FALSE] %*% vector))
  c(estimate = estimate, standard_error = standard_error, ci_low = estimate - 1.96 * standard_error, ci_high = estimate + 1.96 * standard_error)
}

run_diagnostics_predictions_and_gate <- function(data_path, specification_path, grid_path, contrasts_path, model_dir, chapter14_stability_path, output_dir) {
  data <- prepare_data_ch17(read_tsv_ch17(data_path)); specification <- yaml::read_yaml(specification_path); grid <- read_tsv_ch17(grid_path); focal <- read_tsv_ch17(contrasts_path)
  if (!all(c(data$data_status, grid$data_status, focal$data_status, specification$data_status) == STATUS_CH17)) stop("Chapter 17 inputs must remain explicitly synthetic")
  attempts <- read_tsv_ch17(file.path(model_dir, "model_attempts.tsv")); candidates <- c("speaker_slope", "speaker_intercept", "fixed_only"); available <- candidates[file.exists(file.path(model_dir, paste0(candidates, ".rds")))]
  if (!length(available)) stop("No fitted Chapter 17 model is available. Run the first notebook.")
  selected <- available[[1]]; model <- readRDS(file.path(model_dir, paste0(selected, ".rds")))
  residuals <- stats::residuals(model, type = if (inherits(model, "lme")) "pearson" else "response")
  fitted <- stats::fitted(model); if (is.matrix(fitted)) fitted <- fitted[, ncol(fitted)]
  diagnostics <- data.frame(metric = c("observations", "rmse", "residual_mean", "residual_sd", "residual_q025", "residual_median", "residual_q975"), value = c(length(residuals), sqrt(mean(residuals^2)), mean(residuals), stats::sd(residuals), stats::quantile(residuals, .025), stats::median(residuals), stats::quantile(residuals, .975)), interpretation = c("analysis rows", "model-scale residual magnitude", "center check", "residual spread", "lower tail", "center", "upper tail"), data_status = STATUS_CH17)
  condition_spread <- stats::aggregate(residuals, list(condition = data$condition), stats::sd); names(condition_spread)[2] <- "residual_sd"
  condition_spread$data_status <- STATUS_CH17
  item_levels <- levels(data$item_id)
  full_contrast <- contrast_estimate_ch17(model, "SHIFT_A", "BASE", item_levels)
  influence_rows <- list()
  for (speaker in levels(data$speaker_id)) {
    subset <- droplevels(data[data$speaker_id != speaker, ])
    refit <- if (selected == "speaker_slope") capture_fit_ch17(nlme::lme(fixed_formula_ch17, random = ~condition | speaker_id, data = subset, method = "REML", control = nlme::lmeControl(maxIter = 100, msMaxIter = 150, returnObject = TRUE, opt = "optim"))) else if (selected == "speaker_intercept") capture_fit_ch17(nlme::lme(fixed_formula_ch17, random = ~1 | speaker_id, data = subset, method = "REML", control = nlme::lmeControl(maxIter = 100, msMaxIter = 150, returnObject = TRUE, opt = "optim"))) else capture_fit_ch17(stats::lm(fixed_formula_ch17, data = subset))
    estimate <- NA_real_; se <- NA_real_
    if (!is.null(refit$fit)) { value <- contrast_estimate_ch17(refit$fit, "SHIFT_A", "BASE", levels(subset$item_id)); estimate <- value[["estimate"]]; se <- value[["standard_error"]] }
    influence_rows[[length(influence_rows) + 1]] <- data.frame(omitted_speaker = speaker, model_status = ifelse(is.null(refit$fit), "failed", "fit"), contrast_estimate = estimate, standard_error = se, change_from_full = estimate - full_contrast[["estimate"]], warning = refit$warning, error = refit$error, data_status = STATUS_CH17)
  }
  influence <- do.call(rbind, influence_rows)
  support_ranges <- stats::aggregate(speaking_rate_z ~ condition, data, function(x) c(min = min(x), max = max(x), n = length(x)))
  prediction_rows <- list(); support_rows <- list(); beta <- fixed_coefficients_ch17(model); coefficient_names <- names(beta)
  for (i in seq_len(nrow(grid))) {
    condition <- grid$condition[[i]]; rate <- as.numeric(grid$speaking_rate_z[[i]])
    vector <- average_vector_ch17(condition, rate, item_levels, coefficient_names); population <- sum(vector * beta)
    conditional_data <- data.frame(condition = factor(rep(condition, length(item_levels)), levels = levels(data$condition)), speaking_rate_z = rate, item_id = factor(item_levels, levels = item_levels), speaker_id = factor(rep(levels(data$speaker_id)[1], length(item_levels)), levels = levels(data$speaker_id)))
    conditional <- if (inherits(model, "lme")) mean(stats::predict(model, newdata = conditional_data, level = 1)) else population
    observed <- data[data$condition == condition, "speaking_rate_z"]
    extrapolated <- rate < min(observed) || rate > max(observed); nearby <- sum(abs(observed - rate) <= .5)
    prediction_rows[[length(prediction_rows) + 1]] <- data.frame(prediction_id = grid$prediction_id[[i]], condition = condition, speaking_rate_z = rate, population_prediction = population, conditional_prediction_first_speaker = conditional, prediction_scale = "identity-link response scale", averaging_distribution = "equal weight over 18 observed items", extrapolated = extrapolated, weak_support = nearby < 20, data_status = STATUS_CH17)
    support_rows[[length(support_rows) + 1]] <- data.frame(prediction_id = grid$prediction_id[[i]], condition = condition, speaking_rate_z = rate, observed_min = min(observed), observed_max = max(observed), observations_within_half_sd = nearby, extrapolated = extrapolated, weak_support = nearby < 20, data_status = STATUS_CH17)
  }
  predictions <- do.call(rbind, prediction_rows); prediction_support <- do.call(rbind, support_rows)
  contrast_rows <- list()
  for (i in seq_len(nrow(focal))) {
    value <- contrast_estimate_ch17(model, focal$numerator[[i]], focal$denominator[[i]], item_levels)
    contrast_rows[[i]] <- data.frame(contrast_id = focal$contrast_id[[i]], numerator = focal$numerator[[i]], denominator = focal$denominator[[i]], estimate = value[["estimate"]], standard_error = value[["standard_error"]], ci_low = value[["ci_low"]], ci_high = value[["ci_high"]], analysis_scale = focal$analysis_scale[[i]], response_scale = "same as analysis scale under identity link", averaging_distribution = focal$averaging_distribution[[i]], significance_vote_permitted = FALSE, data_status = STATUS_CH17)
  }
  contrasts <- do.call(rbind, contrast_rows)
  if (!file.exists(chapter14_stability_path)) stop("Chapter 14 stability output is required; run its second notebook first.")
  stability <- read_tsv_ch17(chapter14_stability_path)
  chapter14_link <- list(path = normalizePath(chapter14_stability_path), data_status = unique(stability$data_status), stable_dimensions = as.character(stability$dimension[as.character(stability$stable) == "TRUE"]), role = "synthetic teaching linkage only; not empirical validation")
  successful_influence <- influence[is.finite(influence$contrast_estimate), ]
  max_change <- max(abs(successful_influence$change_from_full))
  gate <- list(data_status = STATUS_CH17, decision = "restrict", selected_model = selected, permitted_claim = "In this generated sample, the model estimates condition contrasts averaged over the 18 observed items; new-speaker extension is conditional on the fitted speaker random-effects structure.", prohibited_claims = c("generalization to new items", "empirical phonetic conclusion", "claim selection by significance voting"), new_unit_scope = list(speakers = selected != "fixed_only", items = FALSE), support = list(extrapolated_grid_rows = sum(predictions$extrapolated), weak_support_grid_rows = sum(predictions$weak_support), maximum_leave_one_speaker_change = max_change), chapter14_stability_link = chapter14_link, significance_vote_permitted = FALSE, rationale = c("item is a fixed blocking factor rather than a sampled random effect", "all data and Chapter 14 stability results are synthetic teaching fixtures", "prediction support is reported separately from model computation"))
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  write_tsv_ch17(influence, file.path(output_dir, "cluster_influence.tsv")); write_tsv_ch17(prediction_support, file.path(output_dir, "prediction_support.tsv")); write_tsv_ch17(predictions, file.path(output_dir, "model_predictions.tsv")); write_tsv_ch17(contrasts, file.path(output_dir, "focal_contrasts.tsv")); yaml::write_yaml(gate, file.path(output_dir, "structured_regression_gate.yaml"))
  report <- paste0("<!doctype html><meta charset='utf-8'><title>Chapter 17 model diagnostics</title><h1>Model diagnostics</h1><p><strong>Data status:</strong> SYNTHETIC_TEACHING_FIXTURE. Diagnostics do not license an empirical claim.</p><h2>Global diagnostics</h2>", html_table_ch17(diagnostics), "<h2>Residual spread by condition</h2>", html_table_ch17(condition_spread), "<h2>Model attempts</h2>", html_table_ch17(attempts))
  writeLines(report, file.path(output_dir, "model_diagnostics.html"), useBytes = TRUE)
  decisions <- list(decision = gate$decision, selected_model = selected, extrapolated_grid_rows = sum(predictions$extrapolated), weak_support_grid_rows = sum(predictions$weak_support), leave_one_speaker_fits = nrow(successful_influence), item_scope = "observed_items_only", chapter14_link_status = chapter14_link$data_status, significance_vote_permitted = FALSE)
  write_provenance_ch17(file.path(output_dir, "run_provenance.json"), "run_diagnostics_predictions_and_gate", c(data_path, specification_path, grid_path, contrasts_path, file.path(model_dir, paste0(selected, ".rds")), chapter14_stability_path), decisions)
  list(diagnostics = diagnostics, condition_spread = condition_spread, influence = influence, support = prediction_support, predictions = predictions, contrasts = contrasts, gate = gate, decisions = decisions)
}
