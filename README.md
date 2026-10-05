# Phonetic Research in Practice — companion materials

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23145707.svg)](https://doi.org/10.5281/zenodo.23145707)

Code, synthetic teaching data, and notebooks for the hands-on exercises in *Phonetic Research in Practice: From Research Questions to Reproducible Evidence* by Takeshi Ishihara.

The exercises refer to files by paths that begin with `companion/`, for example `companion/data/ch10/synthetic_acoustics/`. Clone or download this repository and run the exercises from its root directory, so that those paths resolve as printed in the book.

## Contents

| Folder | What it holds |
|---|---|
| `companion/data/` | Synthetic teaching fixtures for Chapters 7–20 (WAV, TSV, YAML), with `MANIFEST.tsv` recording the source, license, and SHA-256 checksum of every file |
| `companion/exercises/` | Complete code for the hands-on exercises, one script per exercise and language; the book prints short excerpts from these files. Example inputs for exercises that start from learner-made files are in `examples/` subfolders |
| `companion/notebooks/` | Twenty-eight notebooks, two per chapter for Chapters 7–20, each with a README that states its inputs, outputs, and checks |
| `companion/src/`, `companion/r/` | Python and R code used by the notebooks |
| `companion/scripts/` | Fixture generators, notebook runners, and the validation entry point |
| `companion/tests/` | Python and R tests |
| `companion/templates/` | Blank records: metadata, sampling, annotation, measurement, and release templates |
| `companion/outputs/` | Reference outputs from a clean local run |
| `companion/instructor/` | Instructor guide, exercise notes, and accessibility guide |

Every data file is generated numerically by the scripts in `companion/scripts/`. The repository contains no recordings of people, no participant information, and no material from licensed corpora.

## Requirements and validation

Python 3.12 or later with the packages in `companion/requirements-python.txt`, and R 4.6 with the packages in `companion/requirements-r.txt`. The exercises in the book also use Praat, Parselmouth, the tidyverse, `lme4`, `lmerTest`, `glmmTMB`, `emmeans`, `mgcv`, `itsadug`, `brms`, `irr`, and the Montreal Forced Aligner; install those as each exercise requires.

Run an exercise script from the repository root, for example `python3 companion/exercises/ch10/ex10_2.py`. To run all of them in clean working directories, use `sh companion/scripts/run_exercise_scripts.sh`.

To regenerate the fixtures, run every test, and execute every notebook in a clean process:

```bash
python3 -m pip install -r companion/requirements-python.txt
sh companion/scripts/validate_implemented_companions.sh
```

The same check runs on GitHub Actions for Ubuntu and macOS.

## License

Free to use, adapt, and redistribute, including for teaching.

- Code (`companion/src/`, `companion/r/`, `companion/scripts/`, `companion/tests/`, and the code cells of the notebooks): MIT License, in `LICENSE`.
- Data, templates, instructor materials, reference outputs, and the written parts of the notebooks: Creative Commons Attribution 4.0 International, in `LICENSE-DATA.txt`.

See `companion/NOTICE.md` for the scope of each license. The license covers this repository only. It does not cover the text of the book, and it does not authorize redistribution of any corpus you apply the code to.

## Citation

Please cite the version you used. Each tagged release is archived on Zenodo with its own DOI; the concept DOI [10.5281/zenodo.23145707](https://doi.org/10.5281/zenodo.23145707) always resolves to the latest version, version 1.1.1 is [10.5281/zenodo.23169367](https://doi.org/10.5281/zenodo.23169367), version 1.1.0 is [10.5281/zenodo.23150151](https://doi.org/10.5281/zenodo.23150151), and version 1.0.0 is [10.5281/zenodo.23145708](https://doi.org/10.5281/zenodo.23145708). Citation metadata is in `CITATION.cff`.

> Ishihara, T. (2026). *Phonetic Research in Practice: Companion materials* (Version 1.1.1) [Computer software and data]. Zenodo. https://doi.org/10.5281/zenodo.23169367
