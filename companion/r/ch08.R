required_packages <- c("digest", "jsonlite", "yaml")
missing_packages <- required_packages[!vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing_packages) > 0) {
  stop("Missing required R packages: ", paste(missing_packages, collapse = ", "))
}

read_tsv <- function(path) {
  utils::read.delim(path, sep = "\t", quote = "", stringsAsFactors = FALSE, check.names = FALSE)
}

write_tsv <- function(data, path) {
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  utils::write.table(data, path, sep = "\t", quote = FALSE, row.names = FALSE, na = "")
}

assert_columns <- function(data, required, label) {
  missing <- setdiff(required, names(data))
  if (length(missing) > 0) {
    stop(label, " is missing columns: ", paste(missing, collapse = ", "))
  }
}

sha256_file <- function(path) {
  digest::digest(file = path, algo = "sha256", serialize = FALSE)
}

write_provenance <- function(path, tool, inputs, decisions) {
  payload <- list(
    tool = tool,
    tool_version = "0.1.0",
    r_version = R.version.string,
    run_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE),
    input_hashes = stats::setNames(lapply(inputs, sha256_file), normalizePath(inputs)),
    decisions = decisions
  )
  jsonlite::write_json(payload, path, pretty = TRUE, auto_unbox = TRUE)
}

html_table <- function(data) {
  escape <- function(value) {
    value <- gsub("&", "&amp;", as.character(value), fixed = TRUE)
    value <- gsub("<", "&lt;", value, fixed = TRUE)
    gsub(">", "&gt;", value, fixed = TRUE)
  }
  header <- paste0("<th>", escape(names(data)), "</th>", collapse = "")
  rows <- apply(data, 1, function(row) {
    paste0("<tr>", paste0("<td>", escape(row), "</td>", collapse = ""), "</tr>")
  })
  paste0("<table border='1'><thead><tr>", header, "</tr></thead><tbody>", paste(rows, collapse = ""), "</tbody></table>")
}

fit_psychometric <- function(data, scope, participant_code = NA_character_) {
  warnings <- character()
  fit <- withCallingHandlers(
    stats::glm(binary_response ~ continuum_step, family = stats::binomial(), data = data),
    warning = function(warning) {
      warnings <<- c(warnings, conditionMessage(warning))
      invokeRestart("muffleWarning")
    }
  )
  coefficients <- stats::coef(fit)
  covariance <- stats::vcov(fit)
  intercept <- unname(coefficients[[1]])
  slope <- unname(coefficients[[2]])
  location <- if (is.finite(slope) && abs(slope) > 1e-10) -intercept / slope else NA_real_
  gradient <- c(-1 / slope, intercept / (slope ^ 2))
  variance_location <- if (all(is.finite(gradient)) && all(is.finite(covariance))) {
    as.numeric(t(gradient) %*% covariance %*% gradient)
  } else {
    NA_real_
  }
  se_location <- if (is.finite(variance_location) && variance_location >= 0) sqrt(variance_location) else NA_real_
  flags <- character()
  if (!isTRUE(fit$converged)) flags <- c(flags, "nonconverged")
  if (!is.finite(slope) || slope <= 0) flags <- c(flags, "nonmonotonic_or_reverse")
  if (length(unique(data$continuum_step)) < 5) flags <- c(flags, "poor_continuum_support")
  if (length(warnings) > 0) flags <- c(flags, paste0("fit_warning:", paste(unique(warnings), collapse = "|")))
  if (length(flags) == 0) flags <- "none"
  data.frame(
    scope = scope,
    participant_code = participant_code,
    trials = nrow(data),
    intercept_logit = intercept,
    slope_logit_per_step = slope,
    location_step = location,
    se_location = se_location,
    location_ci_low = location - 1.96 * se_location,
    location_ci_high = location + 1.96 * se_location,
    converged = isTRUE(fit$converged),
    diagnostic_flag = paste(flags, collapse = ";"),
    stringsAsFactors = FALSE
  )
}

run_psychometric_analysis <- function(trial_manifest_path, stimulus_manifest_path, response_path, output_dir) {
  trials <- read_tsv(trial_manifest_path)
  stimuli <- read_tsv(stimulus_manifest_path)
  responses <- read_tsv(response_path)
  assert_columns(trials, c("trial_id", "participant_code", "stimulus_id", "continuum_step", "data_status"), "trial manifest")
  assert_columns(stimuli, c("stimulus_id", "asset_path", "sha256", "data_status"), "stimulus manifest")
  assert_columns(responses, c("trial_id", "binary_response", "data_status"), "response data")
  if (anyDuplicated(trials$trial_id) || anyDuplicated(responses$trial_id)) stop("trial_id must be unique")
  if (!all(c(trials$data_status, stimuli$data_status, responses$data_status) == "SYNTHETIC_TEACHING_FIXTURE")) {
    stop("Bundled Chapter 8 fixture must remain explicitly synthetic")
  }
  asset_root <- dirname(stimulus_manifest_path)
  asset_hash_observed <- vapply(stimuli$asset_path, function(path) sha256_file(file.path(asset_root, path)), character(1))
  if (!all(tolower(asset_hash_observed) == tolower(stimuli$sha256))) stop("Stimulus asset hash mismatch")
  data <- merge(trials, responses[, c("trial_id", "binary_response", "rt_ms")], by = "trial_id", all = FALSE)
  if (nrow(data) != nrow(trials)) stop("Trial and response join is incomplete")
  if (!all(data$binary_response %in% c(0, 1))) stop("binary_response must contain only 0 and 1")

  group_parameters <- fit_psychometric(data, "group_descriptive")
  participant_parameters <- do.call(rbind, lapply(split(data, data$participant_code), function(participant_data) {
    fit_psychometric(participant_data, "participant", participant_data$participant_code[[1]])
  }))
  parameters <- rbind(group_parameters, participant_parameters)
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  write_tsv(parameters, file.path(output_dir, "psychometric_parameters.tsv"))

  observed <- stats::aggregate(binary_response ~ participant_code + continuum_step, data, mean)
  flagged <- parameters[parameters$diagnostic_flag != "none", , drop = FALSE]
  report <- paste0(
    "<!doctype html><meta charset='utf-8'><title>Psychometric diagnostics</title>",
    "<h1>Psychometric diagnostics</h1>",
    "<p><strong>Data status:</strong> SYNTHETIC_TEACHING_FIXTURE. Numerical tones are not speech and cannot demonstrate categorical perception.</p>",
    "<h2>Parameter summaries</h2>", html_table(parameters),
    "<h2>Observed participant functions</h2>", html_table(observed),
    "<h2>Functions requiring review</h2>", if (nrow(flagged)) html_table(flagged) else "<p>None.</p>"
  )
  writeLines(report, file.path(output_dir, "psychometric_diagnostics.html"), useBytes = TRUE)
  decisions <- list(
    schema_version = "0.1",
    data_status = "SYNTHETIC_TEACHING_FIXTURE",
    probability = "P(binary_response=1 | continuum_step)",
    model = "trial-level logistic regression",
    pooling = "group descriptive fit plus separate participant fits",
    lapse_model = "not estimated in baseline",
    continuum_requirement = "at least five distinct steps",
    nonmonotonic_rule = "flag slope <= 0; do not force a threshold",
    interpretive_limit = "response functions do not by themselves establish categorical perception"
  )
  yaml::write_yaml(decisions, file.path(output_dir, "analysis_decisions.yaml"))
  write_provenance(
    file.path(output_dir, "run_provenance.json"),
    "run_psychometric_analysis",
    c(trial_manifest_path, stimulus_manifest_path, response_path),
    decisions
  )
  list(parameters = parameters, observed = observed, decisions = decisions)
}

run_signal_detection_analysis <- function(event_log_path, decision_path, timing_audit_path, output_dir) {
  events <- read_tsv(event_log_path)
  decisions <- yaml::read_yaml(decision_path)
  timing_audit <- read_tsv(timing_audit_path)
  assert_columns(
    events,
    c("event_id", "participant_code", "condition_id", "signal_present", "yes_response", "correct", "rt_ms", "rt_origin", "data_status"),
    "event log"
  )
  if (anyDuplicated(events$event_id)) stop("event_id must be unique")
  if (!all(events$data_status == "SYNTHETIC_TEACHING_FIXTURE")) stop("Bundled event log must remain explicitly synthetic")
  minimum_rt <- as.numeric(decisions$reaction_time$minimum_ms)
  maximum_rt <- as.numeric(decisions$reaction_time$maximum_ms)
  required_origin <- decisions$reaction_time$origin
  exclusion_reason <- ifelse(
    events$rt_origin != required_origin, "rt_origin_mismatch",
    ifelse(events$rt_ms < minimum_rt, "rt_below_minimum", ifelse(events$rt_ms > maximum_rt, "rt_above_maximum", ""))
  )
  events$exclusion_reason <- exclusion_reason
  excluded <- events[events$exclusion_reason != "", , drop = FALSE]
  included <- events[events$exclusion_reason == "", , drop = FALSE]

  summarize_condition <- function(condition_data) {
    signal <- condition_data[condition_data$signal_present == 1, , drop = FALSE]
    noise <- condition_data[condition_data$signal_present == 0, , drop = FALSE]
    hits <- sum(signal$yes_response == 1)
    misses <- sum(signal$yes_response == 0)
    false_alarms <- sum(noise$yes_response == 1)
    correct_rejections <- sum(noise$yes_response == 0)
    hit_rate <- (hits + 0.5) / (nrow(signal) + 1)
    false_alarm_rate <- (false_alarms + 0.5) / (nrow(noise) + 1)
    z_hit <- stats::qnorm(hit_rate)
    z_false_alarm <- stats::qnorm(false_alarm_rate)
    correct_rt <- condition_data$rt_ms[condition_data$correct == 1]
    data.frame(
      condition_id = condition_data$condition_id[[1]],
      hits = hits,
      misses = misses,
      false_alarms = false_alarms,
      correct_rejections = correct_rejections,
      hit_rate_corrected = hit_rate,
      false_alarm_rate_corrected = false_alarm_rate,
      d_prime = z_hit - z_false_alarm,
      criterion_c = -0.5 * (z_hit + z_false_alarm),
      accuracy = mean(condition_data$correct),
      median_correct_rt_ms = stats::median(correct_rt),
      q10_correct_rt_ms = unname(stats::quantile(correct_rt, 0.10)),
      q90_correct_rt_ms = unname(stats::quantile(correct_rt, 0.90)),
      included_events = nrow(condition_data),
      stringsAsFactors = FALSE
    )
  }
  summary <- do.call(rbind, lapply(split(included, included$condition_id), summarize_condition))
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  write_tsv(summary, file.path(output_dir, "signal_detection_summary.tsv"))
  write_tsv(excluded, file.path(output_dir, "excluded_events.tsv"))
  write_tsv(timing_audit, file.path(output_dir, "online_experiment_audit.tsv"))
  report <- paste0(
    "<!doctype html><meta charset='utf-8'><title>Signal detection and reaction-time diagnostics</title>",
    "<h1>Signal detection and reaction-time diagnostics</h1>",
    "<p><strong>Data status:</strong> SYNTHETIC_TEACHING_FIXTURE. The counts demonstrate decomposition and are not estimates of human performance.</p>",
    "<h2>Condition summary</h2>", html_table(summary),
    "<h2>Excluded events</h2><p>", nrow(excluded), " events excluded under the declared timing rule.</p>",
    "<h2>Synthetic configuration timing audit</h2>", html_table(timing_audit)
  )
  writeLines(report, file.path(output_dir, "reaction_time_diagnostics.html"), useBytes = TRUE)
  yaml::write_yaml(decisions, file.path(output_dir, "analysis_decisions.yaml"))
  write_provenance(
    file.path(output_dir, "run_provenance.json"),
    "run_signal_detection_analysis",
    c(event_log_path, decision_path, timing_audit_path),
    decisions
  )
  list(summary = summary, excluded = excluded, timing_audit = timing_audit, decisions = decisions)
}
