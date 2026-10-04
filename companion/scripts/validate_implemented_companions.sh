#!/bin/sh
set -eu

root_dir=$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)
cd "$root_dir"

python3 companion/scripts/generate_ch07_fixture.py
python3 companion/scripts/generate_ch08_fixture.py
python3 companion/scripts/generate_ch09_fixture.py
python3 companion/scripts/generate_ch10_fixture.py
python3 companion/scripts/generate_ch11_fixture.py
python3 companion/scripts/generate_ch12_fixture.py
python3 companion/scripts/generate_ch13_fixture.py
python3 companion/scripts/generate_ch14_fixture.py
python3 companion/scripts/generate_ch15_fixture.py
python3 companion/scripts/generate_ch16_fixture.py
python3 companion/scripts/generate_ch17_fixture.py
python3 companion/scripts/generate_ch18_fixture.py
python3 companion/scripts/generate_ch19_fixture.py
python3 companion/scripts/generate_ch20_fixture.py

python3 companion/scripts/build_ch07_notebooks.py
python3 companion/scripts/build_ch08_notebooks.py
python3 companion/scripts/build_ch09_notebooks.py
python3 companion/scripts/build_ch10_notebooks.py
python3 companion/scripts/build_ch11_notebooks.py
python3 companion/scripts/build_ch12_notebooks.py
python3 companion/scripts/build_ch13_notebooks.py
python3 companion/scripts/build_ch14_notebooks.py
python3 companion/scripts/build_ch15_notebooks.py
python3 companion/scripts/build_ch16_notebooks.py
python3 companion/scripts/build_ch17_notebooks.py
python3 companion/scripts/build_ch18_notebooks.py
python3 companion/scripts/build_ch19_notebooks.py
python3 companion/scripts/build_ch20_notebooks.py

python3 companion/scripts/validate_data_manifest.py
python3 companion/scripts/validate_notebook_portability.py
python3 -m unittest companion/tests/test_ch07.py -v
Rscript --vanilla companion/tests/test_ch08.R
Rscript --vanilla companion/tests/test_ch09.R
python3 -m unittest companion/tests/test_ch10.py -v
Rscript --vanilla companion/tests/test_ch11.R
Rscript --vanilla companion/tests/test_ch12.R
python3 -m unittest companion/tests/test_ch13.py -v
Rscript --vanilla companion/tests/test_ch14.R
python3 -m unittest companion/tests/test_ch15.py -v
python3 -m unittest companion/tests/test_ch16.py -v
Rscript --vanilla companion/tests/test_ch17.R
Rscript --vanilla companion/tests/test_ch18.R
Rscript --vanilla companion/tests/test_ch19.R
python3 -m unittest companion/tests/test_ch20.py -v

for notebook in companion/notebooks/ch07/*.ipynb companion/notebooks/ch10/*.ipynb companion/notebooks/ch13/*.ipynb companion/notebooks/ch15/*.ipynb companion/notebooks/ch16/*.ipynb companion/notebooks/ch20/*.ipynb; do
    python3 companion/scripts/run_notebook.py "$notebook" --workdir .
done
for notebook in companion/notebooks/ch08/*.ipynb companion/notebooks/ch09/*.ipynb companion/notebooks/ch11/*.ipynb companion/notebooks/ch12/*.ipynb companion/notebooks/ch14/*.ipynb companion/notebooks/ch17/*.ipynb companion/notebooks/ch18/*.ipynb companion/notebooks/ch19/*.ipynb; do
    python3 companion/scripts/run_r_notebook.py "$notebook" --workdir .
done

# The manuscript check exists only in the book repository, not in the public companion repository.
if [ -f work/validate_manuscript.sh ]; then
    work/validate_manuscript.sh
fi
