#!/usr/bin/env python3
"""Static portability audit for all generated companion notebooks."""
from __future__ import annotations
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
ABSOLUTE=re.compile(r"/(Users|home|var/folders)/|[A-Za-z]:\\\\")
def main()->int:
 rows=[];failures=[]
 for path in sorted((ROOT/"companion"/"notebooks").glob("ch??/*.ipynb")):
  payload=json.loads(path.read_text(encoding="utf-8"));language=payload.get("metadata",{}).get("kernelspec",{}).get("language","");code=["".join(c.get("source",[])) for c in payload.get("cells",[]) if c.get("cell_type")=="code"];text="\n".join(code)
  checks={"nbformat4":payload.get("nbformat")==4,"declared_kernel":language in {"python","R"},"code_cells_present":bool(code),"no_absolute_private_path":not ABSOLUTE.search(text),"no_magics_or_shell":not any(line.lstrip().startswith(("%","!")) for source in code for line in source.splitlines()),"no_saved_outputs":all(not c.get("outputs") for c in payload.get("cells",[]) if c.get("cell_type")=="code"),"repository_discovery":("REPOSITORY_ROOT" in text or "find_repository" in text),"synthetic_or_access_status_visible":any(token in path.read_text(encoding="utf-8") for token in ("SYNTHETIC_TEACHING_FIXTURE","INTERNAL CANDIDATE"))}
  failed=[name for name,value in checks.items() if not value];rows.append((path.relative_to(ROOT),language,failed));failures.extend((path,name) for name in failed)
 print(f"notebooks={len(rows)}")
 for path,language,failed in rows:print(f"{path}\t{language}\t{'PASS' if not failed else 'FAIL:'+','.join(failed)}")
 if len(rows)!=28:print(f"Expected 28 notebooks; found {len(rows)}",file=sys.stderr);return 1
 if failures:
  for path,name in failures:print(f"{path}: {name}",file=sys.stderr)
  return 1
 print("PASS notebook portability audit")
 return 0
if __name__=="__main__":raise SystemExit(main())
