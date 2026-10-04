# Chapter 7 notebook specification

**Primary language:** Python

**Implementation status:** Both specified notebooks are implemented as valid notebook files, use the explicitly synthetic Chapter 7 fixture by default, and pass the repository's local sequential-cell runner and unit tests. The dependency lock currently contains only PyYAML; publication-platform and Colab verification remain part of P-001.

Chapter 7 uses local or synthetic audio only. No notebook will request upload of identifiable or licensed research recordings to a hosted service. The local execution path is the default for real study data.

## `01_recording_qc.ipynb`

This notebook ingests a directory of WAV files and a file manifest. It checks file readability, sample rate, bit depth, channel count, duration, peak level, possible digital clipping, silent or near-silent files, and unexpected differences within a session. Learners inspect waveforms and spectra for selected flags and assign measure-specific usability rather than one global quality label.

Required inputs are lossless audio and a manifest with `file_id`, `session_id`, `source_path`, `expected_sample_rate_hz`, `expected_bit_depth`, and `expected_channels`. Outputs are `recording_qc.tsv`, `recording_qc_summary.html`, and `run_provenance.json`. The notebook must not modify source audio.

The notebook supports Exercises 7.1 and 7.2. Its central assessment is a written comparison explaining why a file may pass for one measure and fail for another.

## `02_calibration_and_metadata.ipynb`

This notebook validates a completed recording-session metadata record against the chapter template, extracts technical properties from linked audio, checks that calibration and synchronization records exist when the claim requires them, and estimates simple offset or clock drift from supplied synthetic events. It writes a normalized session record and a list of unresolved deviations.

Required inputs are `recording_session_metadata.yaml`, a file manifest, and optional calibration or event tables. Outputs are `validated_session_metadata.json`, `recording_deviations.tsv`, `timing_check.tsv`, and `run_provenance.json`. A successful run means that the record is internally consistent; it does not certify that the equipment is accurate.

The notebook supports Exercises 7.3 and 7.4. Learners must write a pre-departure decision stating whether to accept, re-record, restrict measures, or stop the session.
