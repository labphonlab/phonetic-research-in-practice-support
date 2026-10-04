#!/usr/bin/env python3
"""Execute R code cells from a notebook in one clean Rscript process."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook", type=Path)
    parser.add_argument("--workdir", type=Path, default=Path.cwd())
    arguments = parser.parse_args()
    payload = json.loads(arguments.notebook.read_text(encoding="utf-8"))
    code_cells = ["".join(cell.get("source", [])) for cell in payload.get("cells", []) if cell.get("cell_type") == "code"]
    if not code_cells:
        raise ValueError(f"No R code cells found in {arguments.notebook}")
    for index, source in enumerate(code_cells, start=1):
        if any(line.lstrip().startswith(("%", "!")) for line in source.splitlines()):
            raise RuntimeError(f"Unsupported notebook magic or shell escape in code cell {index}")
    script = "\n\n".join(
        ["options(warn = 1)"]
        + [f'cat("BEGIN CODE CELL {index}\\n")\n{source}' for index, source in enumerate(code_cells, start=1)]
    )
    with tempfile.NamedTemporaryFile("w", suffix=".R", encoding="utf-8", delete=False) as temporary:
        temporary.write(script)
        temporary_path = Path(temporary.name)
    try:
        completed = subprocess.run(
            ["Rscript", "--vanilla", str(temporary_path)],
            cwd=arguments.workdir,
            check=False,
            text=True,
        )
    finally:
        temporary_path.unlink(missing_ok=True)
    if completed.returncode == 0:
        print(f"PASS {arguments.notebook}")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
