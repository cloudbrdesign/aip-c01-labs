#!/usr/bin/env python3
"""
Episode 5 lab - preflight.

Verifies only what this lab needs. It does not look for AWS credentials, does not read AWS
config or profile files, does not touch the network, and creates nothing.
"""

import json
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
REQUIRED = [
    "my_design.json",
    "rules_sources.json",
    "prompts_with_reference.jsonl",
    "prompts_no_reference.jsonl",
    "scripts/check_design.py",
    "LAB_GUIDE.md",
    "SCENARIO.md",
    "RULES.md",
]
MIN_PY = (3, 9)


def main():
    print("-" * 78)
    print("Episode 5 lab - preflight")
    print("-" * 78)
    ok = True

    v = sys.version_info
    good = (v.major, v.minor) >= MIN_PY
    print(f"[{'ok ' if good else 'FAIL'}] Python {v.major}.{v.minor}.{v.micro} "
          f"(this lab needs {MIN_PY[0]}.{MIN_PY[1]} or newer)")
    ok &= good

    for rel in REQUIRED:
        exists = (LAB / rel).is_file()
        print(f"[{'ok ' if exists else 'FAIL'}] {rel}")
        ok &= exists

    try:
        json.loads((LAB / "my_design.json").read_text(encoding="utf-8"))
        print("[ok ] my_design.json parses")
    except Exception as exc:
        print(f"[FAIL] my_design.json does not parse: {exc}")
        ok = False

    try:
        reg = json.loads((LAB / "rules_sources.json").read_text(encoding="utf-8"))
        print(f"[ok ] rule register parses ({len(reg['rules'])} enforced, "
              f"{len(reg['not_rules'])} deliberately unenforced)")
    except Exception as exc:
        print(f"[FAIL] rule register does not parse: {exc}")
        ok = False

    print("-" * 78)
    print("AWS credentials  : NOT REQUIRED  (this lab never looks for them)")
    print("Network access   : NOT REQUIRED")
    print("Cloud resources  : NONE")
    print("Expected cost    : $0")
    print("Cleanup          : none - delete the directory if you want the space back")
    print("-" * 78)
    print("PREFLIGHT: PASS" if ok else "PREFLIGHT: FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
