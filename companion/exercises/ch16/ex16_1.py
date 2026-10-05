# Exercise 16.1: Draw the dependency graph
# Research Methods in Phonetics, companion exercise script (MIT License).
# Run from the repository root; the excerpts printed in the book are taken from this file.

import yaml
from graphlib import TopologicalSorter
spec = yaml.safe_load(open("companion/data/ch16/synthetic_pipeline/pipeline_spec.yaml"))
inputs = {i["input_id"] for i in spec["inputs"]}
deps = {s["step_id"]: set(s["depends_on"]) for s in spec["steps"]}
# set()
print(
    "undeclared:",
    {d for ds in deps.values() for d in ds} - inputs
    - set(deps),
)
order = list(TopologicalSorter(
    {**deps, **{i: set() for i in inputs}}
).static_order())
print(" -> ".join(order))
edges = [(d, s) for s, ds in deps.items() for d in ds]
open("graph.mmd", "w").write("flowchart LR\n" + "".join(f"  {a} --> {b}\n" for a, b in edges))
print(len(edges))   # 5
