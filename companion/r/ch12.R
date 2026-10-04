required_packages_ch12 <- c("digest", "jsonlite", "yaml", "mgcv")
missing_packages_ch12 <- required_packages_ch12[!vapply(required_packages_ch12, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing_packages_ch12)) stop("Missing R packages: ", paste(missing_packages_ch12, collapse = ", "))

read_tsv_ch12 <- function(path) utils::read.delim(path, sep = "\t", quote = "", stringsAsFactors = FALSE, check.names = FALSE)
write_tsv_ch12 <- function(data, path) {
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  utils::write.table(data, path, sep = "\t", quote = FALSE, row.names = FALSE, na = "")
}
sha256_ch12 <- function(path) digest::digest(file = path, algo = "sha256", serialize = FALSE)
html_table_ch12 <- function(data) {
  esc <- function(x) {
    x <- gsub("&", "&amp;", as.character(x), fixed = TRUE)
    x <- gsub("<", "&lt;", x, fixed = TRUE)
    gsub(">", "&gt;", x, fixed = TRUE)
  }
  header <- paste0("<th>", esc(names(data)), "</th>", collapse = "")
  body <- apply(data, 1, function(row) paste0("<tr>", paste0("<td>", esc(row), "</td>", collapse = ""), "</tr>"))
  paste0("<table border='1'><thead><tr>", header, "</tr></thead><tbody>", paste(body, collapse = ""), "</tbody></table>")
}
write_provenance_ch12 <- function(path, tool, inputs, decisions) {
  jsonlite::write_json(list(tool = tool, tool_version = "0.1.0", r_version = R.version.string, run_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE), input_hashes = stats::setNames(lapply(inputs, sha256_ch12), normalizePath(inputs)), decisions = decisions), path, pretty = TRUE, auto_unbox = TRUE)
}

run_pitch_trajectory_preparation <- function(source_path, interval_path, landmark_path, frame_path, specification_path, output_dir) {
  raw_hash_before <- sha256_ch12(frame_path)
  sources <- read_tsv_ch12(source_path)
  intervals <- read_tsv_ch12(interval_path)
  landmarks <- read_tsv_ch12(landmark_path)
  frames <- read_tsv_ch12(frame_path)
  specification <- yaml::read_yaml(specification_path)
  if (!all(c(sources$data_status, intervals$data_status, landmarks$data_status, frames$data_status) == "SYNTHETIC_TEACHING_FIXTURE")) stop("Bundled Chapter 12 trajectory fixture must remain explicitly synthetic")
  step_ms <- as.numeric(specification$frame_grid$source_step_ms)
  requested_parts <- lapply(seq_len(nrow(intervals)), function(index) {
    row <- intervals[index, ]
    relative_ms <- seq(0, floor(as.numeric(row$duration_ms) / step_ms) * step_ms, by = step_ms)
    data.frame(token_id = row$token_id, source_id = row$source_id, frame_index = seq_along(relative_ms) - 1L, requested_time_s = as.numeric(row$interval_start_s) + relative_ms / 1000, onset_relative_ms = relative_ms, proportional_time = relative_ms / as.numeric(row$duration_ms), interval_duration_ms = as.numeric(row$duration_ms), stringsAsFactors = FALSE)
  })
  requested <- do.call(rbind, requested_parts)
  requested <- merge(requested, sources[, c("source_id", "speaker_id", "item_id", "condition_id", "source_status")], by = "source_id", all.x = TRUE)
  requested <- merge(requested, landmarks[, c("token_id", "landmark_time_s")], by = "token_id", all.x = TRUE)
  requested$landmark_relative_ms <- (requested$requested_time_s - requested$landmark_time_s) * 1000
  joined <- merge(requested, frames[, c("token_id", "frame_index", "raw_candidate_f0_hz", "selected_f0_hz", "frame_status", "quality_score")], by = c("token_id", "frame_index"), all.x = TRUE)
  if (nrow(joined) != nrow(requested)) stop("Raw-frame join changed requested-frame count")
  joined <- joined[order(joined$token_id, joined$frame_index), ]
  joined$data_status <- "SYNTHETIC_TEACHING_FIXTURE"
  joined$gap_code <- ifelse(is.na(joined$frame_status), ifelse(joined$source_status == "source_failure", "source_failure", "estimator_failure"), ifelse(joined$frame_status == "observed", "", joined$frame_status))
  joined$observed_f0_hz <- suppressWarnings(as.numeric(joined$selected_f0_hz))
  speaker_reference <- stats::aggregate(observed_f0_hz ~ speaker_id, joined, stats::median, na.rm = TRUE)
  names(speaker_reference)[2] <- "speaker_reference_f0_hz"
  joined <- merge(joined, speaker_reference, by = "speaker_id", all.x = TRUE)
  joined <- joined[order(joined$token_id, joined$frame_index), ]
  joined$analysis_f0_hz <- joined$observed_f0_hz
  joined$value_origin <- ifelse(is.finite(joined$observed_f0_hz), "observed", "missing")
  maximum_gap_frames <- floor(as.numeric(specification$preprocessing$interpolation_max_gap_ms) / step_ms)
  eligible_codes <- unlist(specification$preprocessing$interpolation_eligible_codes)
  for (token in unique(joined$token_id)) {
    indices <- which(joined$token_id == token)
    values <- joined$analysis_f0_hz[indices]
    codes <- joined$gap_code[indices]
    missing_positions <- which(!is.finite(values))
    if (length(missing_positions) == 0) next
    missing_runs <- split(missing_positions, cumsum(c(TRUE, diff(missing_positions) != 1)))
    for (run in missing_runs) {
      if (length(run) == 0 || length(run) > maximum_gap_frames || !all(codes[run] %in% eligible_codes)) next
      left <- min(run) - 1; right <- max(run) + 1
      if (left < 1 || right > length(values) || !is.finite(values[left]) || !is.finite(values[right])) next
      values[run] <- stats::approx(c(left, right), c(values[left], values[right]), xout = run)$y
      joined$value_origin[indices[run]] <- "interpolated_estimator_failure"
    }
    joined$analysis_f0_hz[indices] <- values
  }
  joined$analysis_f0_st <- ifelse(is.finite(joined$analysis_f0_hz), 12 * log2(joined$analysis_f0_hz / joined$speaker_reference_f0_hz), NA_real_)
  joined$series_start <- !duplicated(joined$token_id)
  joined$proportion_bin <- cut(joined$proportional_time, breaks = seq(0, 1.000001, 0.1), include.lowest = TRUE, right = FALSE)
  coverage_parts <- split(joined, list(joined$condition_id, joined$proportion_bin), drop = TRUE)
  coverage <- do.call(rbind, lapply(coverage_parts, function(block) data.frame(condition_id = block$condition_id[[1]], proportion_bin = as.character(block$proportion_bin[[1]]), requested_frames = nrow(block), observed_frames = sum(block$value_origin == "observed"), interpolated_frames = sum(block$value_origin == "interpolated_estimator_failure"), missing_frames = sum(!is.finite(block$analysis_f0_hz)), contributing_tokens = length(unique(block$token_id[is.finite(block$analysis_f0_hz)])), stringsAsFactors = FALSE)))
  output_dir <- normalizePath(output_dir, mustWork = FALSE)
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  write_tsv_ch12(joined, file.path(output_dir, "requested_frames.tsv"))
  write_tsv_ch12(joined[, c("token_id", "frame_index", "speaker_id", "item_id", "condition_id", "requested_time_s", "onset_relative_ms", "landmark_relative_ms", "proportional_time", "raw_candidate_f0_hz", "observed_f0_hz", "gap_code", "analysis_f0_hz", "analysis_f0_st", "value_origin", "series_start", "data_status")], file.path(output_dir, "trajectory_preprocessing.tsv"))
  write_tsv_ch12(coverage, file.path(output_dir, "trajectory_coverage.tsv"))
  report <- paste0("<!doctype html><meta charset='utf-8'><title>Trajectory diagnostics</title><h1>Trajectory diagnostics</h1><p><strong>Data status:</strong> SYNTHETIC_TEACHING_FIXTURE. Observed and interpolated values are distinguished, and no row estimates human prosody.</p><h2>Coverage and contribution counts</h2>", html_table_ch12(coverage))
  writeLines(report, file.path(output_dir, "trajectory_diagnostics.html"), useBytes = TRUE)
  decision <- list(data_status = "SYNTHETIC_TEACHING_FIXTURE", primary_time = "proportional", sensitivity_time = c("onset_relative_ms", "landmark_relative_ms"), scaling = specification$scaling$transformation, interpolation = list(maximum_gap_ms = specification$preprocessing$interpolation_max_gap_ms, eligible_codes = eligible_codes), observed_and_reconstructed_distinguished = TRUE, condition_outcome_not_used_for_profile_selection = TRUE, interpretive_limit = "generated contours do not provide empirical prosodic evidence")
  yaml::write_yaml(decision, file.path(output_dir, "preprocessing_decision.yaml"))
  raw_hash_after <- sha256_ch12(frame_path)
  if (raw_hash_before != raw_hash_after) stop("Raw frame estimates changed during preprocessing")
  write_provenance_ch12(file.path(output_dir, "run_provenance.json"), "run_pitch_trajectory_preparation", c(source_path, interval_path, landmark_path, frame_path, specification_path), c(decision, list(raw_sha256_before = raw_hash_before, raw_sha256_after = raw_hash_after)))
  list(prepared = joined, coverage = coverage, decision = decision, raw_unchanged = TRUE)
}

lag1_by_series <- function(residuals, token_ids) {
  values <- vapply(split(residuals, token_ids), function(series) if (length(series) >= 3 && stats::sd(series) > 0) stats::cor(series[-length(series)], series[-1]) else NA_real_, numeric(1))
  values[is.finite(values)]
}

rhythm_metrics <- function(vowels, consonants) {
  total <- sum(vowels) + sum(consonants)
  npvi <- if (length(vowels) > 1) mean(abs(diff(vowels)) / ((vowels[-length(vowels)] + vowels[-1]) / 2)) * 100 else NA_real_
  c(percent_v = sum(vowels) / total * 100, varco_v = stats::sd(vowels) / mean(vowels) * 100, npvi_v = npvi)
}

run_dynamic_models_and_rhythm <- function(prepared_path, segmented_path, model_path, output_dir) {
  prepared <- read_tsv_ch12(prepared_path)
  segmented <- read_tsv_ch12(segmented_path)
  specification <- yaml::read_yaml(model_path)
  if (!all(c(prepared$data_status, segmented$data_status) == "SYNTHETIC_TEACHING_FIXTURE")) stop("Bundled Chapter 12 model fixture must remain explicitly synthetic")
  analysis <- prepared[is.finite(prepared$analysis_f0_st), , drop = FALSE]
  analysis <- analysis[order(analysis$token_id, analysis$frame_index), ]
  analysis$condition_id <- factor(analysis$condition_id)
  analysis$speaker_id <- factor(analysis$speaker_id)
  analysis$item_id <- factor(analysis$item_id)
  analysis$series_start_model <- !duplicated(analysis$token_id)
  model_warnings <- character()
  naive <- withCallingHandlers(
    mgcv::gam(analysis_f0_st ~ condition_id + s(proportional_time, by = condition_id, k = 8), data = analysis, method = "REML"),
    warning = function(warning) {
      model_warnings <<- c(model_warnings, paste("naive:", conditionMessage(warning)))
      invokeRestart("muffleWarning")
    }
  )
  structured <- withCallingHandlers(
    mgcv::bam(analysis_f0_st ~ condition_id + s(proportional_time, by = condition_id, k = 8) + s(speaker_id, bs = "re") + s(item_id, bs = "re") + s(proportional_time, speaker_id, bs = "fs", m = 1, k = 5), data = analysis, method = "fREML", rho = as.numeric(specification$residual_rho), AR.start = analysis$series_start_model, discrete = TRUE),
    warning = function(warning) {
      model_warnings <<- c(model_warnings, paste("structured:", conditionMessage(warning)))
      invokeRestart("muffleWarning")
    }
  )
  grid <- expand.grid(proportional_time = seq(as.numeric(specification$prediction_grid$proportional_start), as.numeric(specification$prediction_grid$proportional_end), by = as.numeric(specification$prediction_grid$step)), condition_id = levels(analysis$condition_id), KEEP.OUT.ATTRS = FALSE, stringsAsFactors = FALSE)
  grid$condition_id <- factor(grid$condition_id, levels = levels(analysis$condition_id))
  grid$speaker_id <- factor(levels(analysis$speaker_id)[1], levels = levels(analysis$speaker_id))
  grid$item_id <- factor(levels(analysis$item_id)[1], levels = levels(analysis$item_id))
  naive_prediction <- stats::predict(naive, grid, se.fit = TRUE)
  structured_prediction <- stats::predict(structured, grid, se.fit = TRUE, exclude = c("s(speaker_id)", "s(item_id)", "s(proportional_time,speaker_id)"))
  predictions <- rbind(
    data.frame(model = "naive_aggregate_smooth", grid[, c("condition_id", "proportional_time")], estimate_st = as.numeric(naive_prediction$fit), se_st = as.numeric(naive_prediction$se.fit), stringsAsFactors = FALSE),
    data.frame(model = "structured_ar1", grid[, c("condition_id", "proportional_time")], estimate_st = as.numeric(structured_prediction$fit), se_st = as.numeric(structured_prediction$se.fit), stringsAsFactors = FALSE)
  )
  naive_lag <- lag1_by_series(stats::residuals(naive), analysis$token_id)
  structured_lag <- lag1_by_series(stats::residuals(structured), analysis$token_id)
  residual_dependence <- rbind(data.frame(model = "naive_aggregate_smooth", token_count = length(naive_lag), mean_lag1 = mean(naive_lag), median_lag1 = stats::median(naive_lag)), data.frame(model = "structured_ar1", token_count = length(structured_lag), mean_lag1 = mean(structured_lag), median_lag1 = stats::median(structured_lag)))
  rhythm_blocks <- split(segmented, list(segmented$speaker_id, segmented$sentence_set, segmented$segmentation_profile), drop = TRUE)
  rhythm_rows <- do.call(rbind, lapply(rhythm_blocks, function(block) {
    metrics <- rhythm_metrics(block$vowel_duration_ms, block$consonant_duration_ms)
    data.frame(speaker_id = block$speaker_id[[1]], sample_group = block$sample_group[[1]], sentence_set = block$sentence_set[[1]], segmentation_profile = block$segmentation_profile[[1]], units = nrow(block), percent_v = metrics[["percent_v"]], varco_v = metrics[["varco_v"]], npvi_v = metrics[["npvi_v"]], data_status = "SYNTHETIC_TEACHING_FIXTURE", stringsAsFactors = FALSE)
  }))
  subsets <- list(all_sets = c("SET_1", "SET_2", "SET_3", "SET_4"), sets_1_2 = c("SET_1", "SET_2"), sets_3_4 = c("SET_3", "SET_4"))
  sensitivity_rows <- list(); sensitivity_index <- 0
  for (speaker in unique(segmented$speaker_id)) for (subset_name in names(subsets)) for (profile in unique(segmented$segmentation_profile)) {
    block <- segmented[segmented$speaker_id == speaker & segmented$sentence_set %in% subsets[[subset_name]] & segmented$segmentation_profile == profile, , drop = FALSE]
    metrics <- rhythm_metrics(block$vowel_duration_ms, block$consonant_duration_ms)
    sensitivity_index <- sensitivity_index + 1
    sensitivity_rows[[sensitivity_index]] <- data.frame(speaker_id = speaker, sample_group = block$sample_group[[1]], material_subset = subset_name, segmentation_profile = profile, percent_v = metrics[["percent_v"]], varco_v = metrics[["varco_v"]], npvi_v = metrics[["npvi_v"]], data_status = "SYNTHETIC_TEACHING_FIXTURE", stringsAsFactors = FALSE)
  }
  sensitivity <- do.call(rbind, sensitivity_rows)
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  write_tsv_ch12(predictions, file.path(output_dir, "trajectory_predictions.tsv"))
  write_tsv_ch12(residual_dependence, file.path(output_dir, "residual_dependence.tsv"))
  write_tsv_ch12(rhythm_rows, file.path(output_dir, "rhythm_metrics_by_unit.tsv"))
  write_tsv_ch12(sensitivity, file.path(output_dir, "rhythm_sensitivity.tsv"))
  warning_rows <- data.frame(
    warning_id = seq_along(unique(model_warnings)),
    message = unique(model_warnings),
    retained_for_review = TRUE,
    data_status = "SYNTHETIC_TEACHING_FIXTURE",
    stringsAsFactors = FALSE
  )
  write_tsv_ch12(warning_rows, file.path(output_dir, "model_warnings.tsv"))
  report <- paste0("<!doctype html><meta charset='utf-8'><title>Dynamic model diagnostics</title><h1>Dynamic model diagnostics</h1><p><strong>Data status:</strong> SYNTHETIC_TEACHING_FIXTURE. Frames are dependent observations, not independent replications.</p><h2>Residual dependence</h2>", html_table_ch12(residual_dependence), "<h2>Rhythm sensitivity design</h2><p>Metrics are retained by speaker, material subset, and segmentation profile; no language is classified.</p>")
  writeLines(report, file.path(output_dir, "dynamic_model_diagnostics.html"), useBytes = TRUE)
  gate <- list(data_status = "SYNTHETIC_TEACHING_FIXTURE", decision = "restrict", reason = "structured model reduces but does not erase serial dependence; conclusions remain synthetic and sample-scoped", independent_units = c("speaker_id", "item_id", "token_id"), frame_count_is_replication_count = FALSE, rhythm_claim = "sample description only", typological_classification_permitted = FALSE)
  yaml::write_yaml(gate, file.path(output_dir, "trajectory_gate.yaml"))
  write_provenance_ch12(file.path(output_dir, "run_provenance.json"), "run_dynamic_models_and_rhythm", c(prepared_path, segmented_path, model_path), c(specification, gate))
  list(predictions = predictions, residual_dependence = residual_dependence, rhythm = rhythm_rows, sensitivity = sensitivity, warnings = warning_rows, gate = gate)
}
