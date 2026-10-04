required_packages_ch11 <- c("digest", "jsonlite", "yaml")
missing_packages_ch11 <- required_packages_ch11[!vapply(required_packages_ch11, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing_packages_ch11)) stop("Missing R packages: ", paste(missing_packages_ch11, collapse = ", "))

read_tsv_ch11 <- function(path) utils::read.delim(path, sep = "\t", quote = "", stringsAsFactors = FALSE, check.names = FALSE)
write_tsv_ch11 <- function(data, path) {
  dir.create(dirname(path), recursive = TRUE, showWarnings = FALSE)
  utils::write.table(data, path, sep = "\t", quote = FALSE, row.names = FALSE, na = "")
}
sha256_ch11 <- function(path) digest::digest(file = path, algo = "sha256", serialize = FALSE)
html_table_ch11 <- function(data) {
  esc <- function(x) {
    x <- gsub("&", "&amp;", as.character(x), fixed = TRUE)
    x <- gsub("<", "&lt;", x, fixed = TRUE)
    gsub(">", "&gt;", x, fixed = TRUE)
  }
  header <- paste0("<th>", esc(names(data)), "</th>", collapse = "")
  body <- apply(data, 1, function(row) paste0("<tr>", paste0("<td>", esc(row), "</td>", collapse = ""), "</tr>"))
  paste0("<table border='1'><thead><tr>", header, "</tr></thead><tbody>", paste(body, collapse = ""), "</tbody></table>")
}
write_provenance_ch11 <- function(path, tool, inputs, decisions) {
  jsonlite::write_json(list(tool = tool, tool_version = "0.1.0", r_version = R.version.string, run_at_utc = format(Sys.time(), tz = "UTC", usetz = TRUE), input_hashes = stats::setNames(lapply(inputs, sha256_ch11), normalizePath(inputs)), decisions = decisions), path, pretty = TRUE, auto_unbox = TRUE)
}

run_segmental_measure_audit <- function(event_dictionary_path, annotation_path, acoustic_path, request_path, output_dir) {
  dictionary <- yaml::read_yaml(event_dictionary_path)
  annotations <- read_tsv_ch11(annotation_path)
  acoustics <- read_tsv_ch11(acoustic_path)
  requests <- read_tsv_ch11(request_path)
  if (!all(c(annotations$data_status, acoustics$data_status, requests$data_status) == "SYNTHETIC_TEACHING_FIXTURE")) stop("Bundled Chapter 11 fixture must remain explicitly synthetic")
  if (anyDuplicated(annotations$token_id) || anyDuplicated(acoustics$token_id) || anyDuplicated(requests$observation_id)) stop("Stable identifiers must be unique")
  annotation_by_token <- split(annotations, annotations$token_id)
  acoustic_by_token <- split(acoustics, acoustics$token_id)
  measure_one <- function(request) {
    annotation <- annotation_by_token[[request$token_id]][1, ]
    acoustic <- acoustic_by_token[[request$token_id]][1, ]
    value <- NA_real_
    start <- NA_real_
    end <- NA_real_
    missingness <- ""
    measure <- request$measure_id
    numeric_or_na <- function(x) if (length(x) == 0 || is.na(x) || x == "") NA_real_ else as.numeric(x)
    if (measure == "vot") {
      start <- numeric_or_na(annotation$release_s); end <- numeric_or_na(annotation$voicing_onset_s); value <- (end - start) * 1000
    } else if (measure == "closure_duration") {
      start <- numeric_or_na(annotation$closure_start_s); end <- numeric_or_na(annotation$release_s); value <- (end - start) * 1000
    } else if (measure == "vowel_onset_f0") {
      value <- numeric_or_na(acoustic$f0_vowel_onset_hz)
    } else if (measure == "vowel_duration") {
      start <- numeric_or_na(annotation$vowel_onset_s); end <- numeric_or_na(annotation$vowel_offset_s); value <- (end - start) * 1000
    } else if (measure == "f1") {
      value <- numeric_or_na(acoustic$f1_hz)
    } else if (measure == "f2") {
      value <- numeric_or_na(acoustic$f2_hz)
    } else if (measure == "f3") {
      value <- numeric_or_na(acoustic$f3_hz)
    } else if (measure == "fricative_duration") {
      start <- numeric_or_na(annotation$fricative_start_s); end <- numeric_or_na(annotation$fricative_end_s); value <- (end - start) * 1000
    } else if (measure == "fricative_cog") {
      value <- numeric_or_na(acoustic$fricative_cog_hz)
    } else stop("Unknown requested measure: ", measure)
    quality <- "ok"
    if (!is.finite(value)) {
      quality <- "missing"
      missingness <- ifelse(annotation$ambiguity_code == "", "required_event_absent", annotation$ambiguity_code)
    } else if (measure != "vot" && !is.na(start) && !is.na(end) && end < start) {
      quality <- "invalid_landmark_order"
      missingness <- "end_before_start"
    } else if (annotation$ambiguity_code != "") {
      quality <- "review"
      missingness <- annotation$ambiguity_code
    }
    data.frame(observation_id = request$observation_id, token_id = request$token_id, speaker_id = request$speaker_id, session_id = request$session_id, measure_id = measure, context_id = request$context_id, token_class = annotation$token_class, vowel_category = annotation$vowel_category, landmark_start_s = start, landmark_end_s = end, raw_value = value, raw_unit = request$raw_unit, quality_status = quality, missingness_code = missingness, provenance_id = request$provenance_id, data_status = "SYNTHETIC_TEACHING_FIXTURE", stringsAsFactors = FALSE)
  }
  raw <- do.call(rbind, lapply(seq_len(nrow(requests)), function(index) measure_one(requests[index, ])))
  audit <- raw[raw$quality_status != "ok", c("observation_id", "token_id", "speaker_id", "measure_id", "quality_status", "missingness_code", "data_status"), drop = FALSE]
  combinations <- split(raw, list(raw$measure_id, raw$context_id), drop = TRUE)
  coverage <- do.call(rbind, lapply(combinations, function(block) data.frame(measure_id = block$measure_id[[1]], context_id = block$context_id[[1]], requested = nrow(block), usable = sum(block$quality_status == "ok"), review = sum(block$quality_status == "review"), missing_or_invalid = sum(block$quality_status %in% c("missing", "invalid_landmark_order")), stringsAsFactors = FALSE)))
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  write_tsv_ch11(raw, file.path(output_dir, "segmental_raw_measures.tsv"))
  write_tsv_ch11(audit, file.path(output_dir, "landmark_audit.tsv"))
  write_tsv_ch11(coverage, file.path(output_dir, "coverage_by_context.tsv"))
  report <- paste0("<!doctype html><meta charset='utf-8'><title>Segmental diagnostics</title><h1>Segmental diagnostics</h1><p><strong>Data status:</strong> SYNTHETIC_TEACHING_FIXTURE. Reconstructed values do not describe speech.</p><h2>Coverage</h2>", html_table_ch11(coverage), "<h2>Requested rows</h2><p>", nrow(raw), " rows retained, including ", nrow(audit), " review or failure rows.</p>")
  writeLines(report, file.path(output_dir, "segmental_diagnostics.html"), useBytes = TRUE)
  decisions <- list(data_status = "SYNTHETIC_TEACHING_FIXTURE", event_dictionary_version = dictionary$schema_version, output_policy = "one row per requested observation including failures", raw_gate = "learner decision required", interpretive_limit = "generated landmarks do not validate a segmental measurement protocol")
  yaml::write_yaml(decisions, file.path(output_dir, "analysis_decisions.yaml"))
  write_provenance_ch11(file.path(output_dir, "run_provenance.json"), "run_segmental_measure_audit", c(event_dictionary_path, annotation_path, acoustic_path, request_path), decisions)
  list(raw = raw, audit = audit, coverage = coverage, decisions = decisions)
}

run_normalization_comparison <- function(raw_path, annotation_path, split_path, request_path, output_dir, bootstrap_replicates = 100L, seed = 11112026L) {
  raw_hash_before <- sha256_ch11(raw_path)
  raw <- read_tsv_ch11(raw_path)
  annotations <- read_tsv_ch11(annotation_path)
  splits <- read_tsv_ch11(split_path)
  requests <- read_tsv_ch11(request_path)
  if (!all(c(raw$data_status, annotations$data_status, splits$data_status, requests$data_status) == "SYNTHETIC_TEACHING_FIXTURE")) stop("Bundled normalization fixture must remain explicitly synthetic")
  formants <- raw[raw$measure_id %in% c("f1", "f2", "f3") & raw$quality_status == "ok", , drop = FALSE]
  category_map <- annotations[, c("token_id", "vowel_category")]
  formants <- merge(formants[, setdiff(names(formants), "vowel_category")], category_map, by = "token_id", all.x = TRUE)
  formants <- merge(formants, splits[, c("speaker_id", "split", "reference_inventory")], by = "speaker_id", all.x = TRUE)
  training <- formants[formants$split == "training", , drop = FALSE]
  speakers <- unique(splits$speaker_id)
  grand_f3 <- stats::median(training$raw_value[training$measure_id == "f3"], na.rm = TRUE)
  parameter_rows <- list()
  parameter_index <- 0
  speaker_eligible <- setNames(logical(length(speakers)), speakers)
  speaker_reason <- setNames(character(length(speakers)), speakers)
  for (speaker in speakers) {
    block <- training[training$speaker_id == speaker, , drop = FALSE]
    counts <- table(block$vowel_category[block$measure_id == "f1"])
    eligible <- nrow(block) > 0 && all(c("i", "a", "u") %in% names(counts)) && all(counts[c("i", "a", "u")] >= 2)
    speaker_eligible[[speaker]] <- eligible
    speaker_reason[[speaker]] <- if (eligible) "eligible_complete_training_inventory" else if (nrow(block) == 0) "evaluation_split_no_training_parameters" else "incomplete_reference_inventory"
    for (measure in c("f1", "f2", "f3")) {
      values <- block$raw_value[block$measure_id == measure]
      parameter_index <- parameter_index + 1
      parameter_rows[[parameter_index]] <- data.frame(speaker_id = speaker, split = splits$split[match(speaker, splits$speaker_id)], measure_id = measure, eligible = eligible, eligibility_reason = speaker_reason[[speaker]], n_reference = length(values), reference_center = if (eligible) mean(values) else NA_real_, reference_scale = if (eligible) stats::sd(values) else NA_real_, speaker_median_f3 = if (eligible) stats::median(block$raw_value[block$measure_id == "f3"]) else NA_real_, grand_training_median_f3 = grand_f3, reference_categories = paste(sort(unique(block$vowel_category)), collapse = ","), stringsAsFactors = FALSE)
    }
  }
  parameters <- do.call(rbind, parameter_rows)
  param_key <- split(parameters, paste(parameters$speaker_id, parameters$measure_id, sep = "|"))
  normalized_rows <- list()
  row_index <- 0
  for (index in seq_len(nrow(formants))) {
    row <- formants[index, ]
    parameter <- param_key[[paste(row$speaker_id, row$measure_id, sep = "|")]][1, ]
    for (transformation in c("raw_hz", "log_hz", "within_speaker_z", "f3_reference_scaling")) {
      row_index <- row_index + 1
      value <- NA_real_
      if (transformation == "raw_hz") value <- row$raw_value
      if (transformation == "log_hz") value <- log(row$raw_value)
      if (transformation == "within_speaker_z" && isTRUE(parameter$eligible) && parameter$reference_scale > 0) value <- (row$raw_value - parameter$reference_center) / parameter$reference_scale
      if (transformation == "f3_reference_scaling" && isTRUE(parameter$eligible)) value <- row$raw_value * parameter$grand_training_median_f3 / parameter$speaker_median_f3
      normalized_rows[[row_index]] <- data.frame(observation_id = row$observation_id, token_id = row$token_id, speaker_id = row$speaker_id, split = row$split, vowel_category = row$vowel_category, measure_id = row$measure_id, raw_value_hz = row$raw_value, transformation_id = transformation, reference_center = if (transformation == "within_speaker_z") parameter$reference_center else NA_real_, reference_scale = if (transformation == "within_speaker_z") parameter$reference_scale else if (transformation == "f3_reference_scaling") parameter$speaker_median_f3 else NA_real_, transformed_value = value, transformed_unit = if (transformation %in% c("raw_hz", "f3_reference_scaling")) "Hz" else if (transformation == "log_hz") "log_Hz" else "z", eligible = parameter$eligible, eligibility_reason = parameter$eligibility_reason, data_status = "SYNTHETIC_TEACHING_FIXTURE", stringsAsFactors = FALSE)
    }
  }
  normalized <- do.call(rbind, normalized_rows)
  set.seed(seed)
  stability_rows <- list(); stability_index <- 0
  for (speaker in speakers[speaker_eligible]) {
    block <- training[training$speaker_id == speaker, , drop = FALSE]
    for (measure in c("f1", "f2", "f3")) {
      values <- block$raw_value[block$measure_id == measure]
      boot_center <- replicate(bootstrap_replicates, mean(sample(values, length(values), replace = TRUE)))
      boot_scale <- replicate(bootstrap_replicates, stats::sd(sample(values, length(values), replace = TRUE)))
      stability_index <- stability_index + 1
      stability_rows[[stability_index]] <- data.frame(speaker_id = speaker, measure_id = measure, bootstrap_replicates = bootstrap_replicates, center_sd = stats::sd(boot_center), scale_sd = stats::sd(boot_scale), seed = seed, data_status = "SYNTHETIC_TEACHING_FIXTURE", stringsAsFactors = FALSE)
    }
  }
  stability <- do.call(rbind, stability_rows)
  rebuild <- normalized[normalized$eligible & normalized$transformation_id %in% c("within_speaker_z", "f3_reference_scaling"), , drop = FALSE]
  rebuilt_values <- ifelse(rebuild$transformation_id == "within_speaker_z", (rebuild$raw_value_hz - rebuild$reference_center) / rebuild$reference_scale, rebuild$raw_value_hz * grand_f3 / rebuild$reference_scale)
  exact_rebuild <- isTRUE(all.equal(rebuilt_values, rebuild$transformed_value, tolerance = 1e-12))
  if (!exact_rebuild) stop("Normalized values cannot be rebuilt from raw values and parameters")
  dir.create(output_dir, recursive = TRUE, showWarnings = FALSE)
  write_tsv_ch11(parameters, file.path(output_dir, "normalization_parameters.tsv"))
  write_tsv_ch11(normalized, file.path(output_dir, "segmental_normalized_measures.tsv"))
  write_tsv_ch11(stability, file.path(output_dir, "normalization_stability.tsv"))
  eligibility <- unique(parameters[, c("speaker_id", "split", "eligible", "eligibility_reason", "reference_categories")])
  report <- paste0("<!doctype html><meta charset='utf-8'><title>Normalization diagnostics</title><h1>Normalization diagnostics</h1><p><strong>Data status:</strong> SYNTHETIC_TEACHING_FIXTURE. Apparent category or speaker differences are generated and not empirical findings.</p><h2>Eligibility</h2>", html_table_ch11(eligibility), "<p>Exact reconstruction from raw values and recorded parameters: ", exact_rebuild, ".</p>")
  writeLines(report, file.path(output_dir, "normalization_diagnostics.html"), useBytes = TRUE)
  decision <- list(data_status = "SYNTHETIC_TEACHING_FIXTURE", estimand = "vowel-category separation within the eligible training-speaker population", preservation_target = "retain within-speaker vowel ordering and raw values", reduction_target = "reduce between-speaker reference-frequency dispersion", reference_sample = "training split only", transformations = c("raw_hz", "log_hz", "within_speaker_z", "f3_reference_scaling"), exact_rebuild = exact_rebuild, interpretive_limit = "synthetic normalization comparison does not establish a universally preferred procedure")
  yaml::write_yaml(decision, file.path(output_dir, "normalization_decision.yaml"))
  raw_hash_after <- sha256_ch11(raw_path)
  if (raw_hash_before != raw_hash_after) stop("Raw measure file changed during normalization")
  write_provenance_ch11(file.path(output_dir, "run_provenance.json"), "run_normalization_comparison", c(raw_path, annotation_path, split_path, request_path), c(decision, list(raw_sha256_before = raw_hash_before, raw_sha256_after = raw_hash_after)))
  list(parameters = parameters, normalized = normalized, stability = stability, decision = decision, exact_rebuild = exact_rebuild, raw_unchanged = raw_hash_before == raw_hash_after)
}
