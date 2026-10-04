# Chapter 13 notebook specification and implementation record

**Primary language:** Python

Chapter 13 treats each articulatory stream as a calibrated spatial and temporal measurement. The notebooks use synthetic calibration objects and trajectories by default and never require redistribution of identifiable or licensed recordings.

## `01_coordinate_and_sync_audit.ipynb`

This notebook reconstructs native, head-corrected, anatomically rotated, and time-corrected coordinates from recorded transforms. It tests rigid reference geometry, probe or sensor drift, offset and clock drift, dropped frames, axis conventions, and residual synchronization error. Learners introduce controlled failures and determine which claims survive.

Required inputs are `multimodal_session.yaml`, stream manifests, native timestamps, calibration and synchronization events, raw reference channels, and transformation matrices. Outputs are `stream_quality.tsv`, `coordinate_transforms.tsv`, `sync_model.tsv`, `sync_residuals.tsv`, `coordinate_sync_diagnostics.html`, and `run_provenance.json`.

The notebook supports Exercises 13.2 and 13.3. It preserves native values and writes every correction to a new layer.

## `02_kinematic_landmarks.ipynb`

This notebook applies prespecified filtering, derivative, and landmark profiles to smooth, plateaued, multi-peaked, noisy, and missing trajectories. It retains all candidate events, distinguishes nonidentifiable landmarks from software failure, and summarizes how profile choice changes the eligible event population.

Required inputs are validated trajectories, event domains, landmark profiles, grouping metadata, and quality decisions. Outputs are `kinematic_candidates.tsv`, `kinematic_landmarks.tsv`, `landmark_availability.tsv`, `landmark_sensitivity.tsv`, `kinematic_diagnostics.html`, `multimodal_gate.yaml`, and `run_provenance.json`.

The notebook supports Exercises 13.1 and 13.4. It ends with stream-specific and combined multimodal decisions rather than one global reliability label.

## Implementation status

Both notebooks, the seven-artifact synthetic fixture, the reusable Python module, four automated tests, and the clean local execution route are implemented. The coordinate notebook reconstructs 952 retained sensor-frame records while preserving native coordinates and timestamps. It detects twenty-seven frames whose reference geometry exceeds the declared tolerance, two dropped frames, and displacement of a nominally stationary target during the drift interval. The synchronization comparison retains one missing anchor: a single-offset model leaves approximately 22.9 ms maximum absolute residual error, whereas the prespecified linear drift model leaves approximately 0.98 ms in this generated fixture.

The kinematic notebook applies four prespecified filter-and-threshold profiles to twenty-four generated events. It retains all velocity candidates and produces ninety-six event-by-profile landmark records. Plateaued, missing, and low-excursion cases are recorded as phonetic nonidentifiability rather than coerced into numeric landmarks. Smooth, noisy, and multi-peaked cases remain eligible with all alternative candidates preserved. The combined gate is `restrict`: the reference-drift interval and dropped frames are excluded, landmark eligibility remains profile-dependent, and no synthetic result is presented as instrument validation.

The fixture is regenerated with `python3 companion/scripts/generate_ch13_fixture.py`, the notebooks with `python3 companion/scripts/build_ch13_notebooks.py`, and the tests with `python3 -m unittest companion/tests/test_ch13.py -v`. Both notebooks pass the clean Python runner in the recorded local environment; Colab, cross-platform, and continuous-integration verification remain open under P-001.
