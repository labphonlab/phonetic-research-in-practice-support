#!/usr/bin/env python3
"""Execute plain Python code cells from a notebook without hidden notebook state.

This intentionally small runner supports the repository's clean local validation
route. It rejects cell magics and executes cells in documented order.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import traceback
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook", type=Path)
    parser.add_argument("--workdir", type=Path, default=Path.cwd())
    arguments = parser.parse_args()

    notebook = json.loads(arguments.notebook.read_text(encoding="utf-8"))
    namespace = {"__name__": "__main__", "__file__": str(arguments.notebook.resolve())}
    original_directory = Path.cwd()
    os.chdir(arguments.workdir)
    try:
        for index, cell in enumerate(notebook.get("cells", []), start=1):
            if cell.get("cell_type") != "code":
                continue
            source = "".join(cell.get("source", []))
            if any(line.lstrip().startswith(("%", "!")) for line in source.splitlines()):
                raise RuntimeError(f"Unsupported notebook magic or shell escape in cell {index}")
            try:
                exec(compile(source, f"{arguments.notebook}:cell-{index}", "exec"), namespace)
            except Exception:
                print(f"Notebook failed in code cell {index}: {arguments.notebook}", file=sys.stderr)
                traceback.print_exc()
                return 1
    finally:
        os.chdir(original_directory)
    print(f"PASS {arguments.notebook}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
