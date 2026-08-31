#!/usr/bin/env python3
"""
Episode 5 lab - measurement design checker.

WHAT THIS IS
    A constraint validator. It reads your design file and your chosen prompt dataset and
    reports whether the configuration satisfies constraints that Amazon Bedrock's own
    documentation states.

WHAT THIS IS NOT
    It is not a recommender, it does not assess the merit of your design, and it does not run
    an evaluation. It will not tell you which measurement to select, it does not rank designs,
    and it never produces or simulates an evaluation result of any kind. It cannot tell you whether your design measures what you set out to
    learn - see N4 in RULES.md.

    No AWS credentials. No network access. No cloud resources. Cost: $0.

Python 3.9+. Standard library only.
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parent

PLACEHOLDER_MARKERS = ("<CHOICE", "CHOOSE_", "REPLACE_ME")


# --------------------------------------------------------------------------------------
# Loading. Syntax handling here is TOOLING HYGIENE, not the exercise. The scaffold ships
# valid; if it stops being valid, that is a mechanical problem to fix, and this checker
# says so in those words rather than treating it as a finding about your design.
# --------------------------------------------------------------------------------------

def load_json(path, label):
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        fail_hard(f"{label} not found at {path}")
    try:
        return json.loads(text)
    except json.JSONDecodeError as exc:
        fail_hard(
            f"TOOLING: {label} is not valid JSON (line {exc.lineno}, column {exc.colno}): {exc.msg}.\n"
            f"         This is a mechanical problem, not a finding about your measurement design.\n"
            f"         The file shipped valid. Restore the structure and edit only the marked values."
        )


def load_jsonl(path, label):
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        fail_hard(f"{label} not found at {path}")
    records = []
    for n, line in enumerate(lines, start=1):
        if not line.strip():
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError as exc:
            fail_hard(
                f"TOOLING: {label} line {n} is not valid JSON: {exc.msg}.\n"
                f"         This is a mechanical problem, not a finding about your measurement design."
            )
    return records


def fail_hard(message):
    print()
    print(message)
    print()
    sys.exit(2)


# --------------------------------------------------------------------------------------
# Findings
# --------------------------------------------------------------------------------------

class Finding:
    def __init__(self, rule_id, detail, weight, source_id, source_title, source_url):
        self.rule_id = rule_id
        self.detail = detail
        self.weight = weight
        self.source_id = source_id
        self.source_title = source_title
        self.source_url = source_url

    def render(self):
        head = f"FAIL  {self.rule_id}  ({self.weight})  {self.detail}"
        cite = f"            source: {self.source_id} - {self.source_title}"
        link = f"            {self.source_url}"
        return "\n".join([head, cite, link])


class Checker:
    def __init__(self, register):
        self.reg = register
        self.findings = []
        self.checked = []

    def source_for(self, rule_id):
        sid = self.reg["rules"][rule_id]["source"]
        s = self.reg["sources"][sid]
        return sid, s["title"], s["url"]

    def note(self, rule_id):
        self.checked.append(rule_id)

    def flag(self, rule_id, detail):
        sid, title, url = self.source_for(rule_id)
        weight = self.reg["rules"][rule_id]["weight"]
        self.findings.append(Finding(rule_id, detail, weight, sid, title, url))


# --------------------------------------------------------------------------------------
# Rules
# --------------------------------------------------------------------------------------

# Documentation keys describe the <CHOICE ...> convention, so they contain the marker text by
# design. Scanning them would report a placeholder the learner can never resolve.
DOC_KEYS = ("_README", "_about", "_comment")


def unresolved_placeholders(obj, trail="design"):
    found = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in DOC_KEYS:
                continue
            found += unresolved_placeholders(v, f"{trail}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            found += unresolved_placeholders(v, f"{trail}[{i}]")
    elif isinstance(obj, str):
        if any(m in obj for m in PLACEHOLDER_MARKERS):
            found.append((trail, obj))
    return found


def run_rules(design, records, dataset_is_builtin, register):
    c = Checker(register)

    auto = design.get("evaluationConfig", {}).get("automated", {})
    configs = auto.get("datasetMetricConfigs", [])
    evaluator = auto.get("evaluatorModelConfig")
    evaluator_present = evaluator not in (None, {}, [])

    # ---- R4: datasetMetricConfigs bounds
    c.note("R4")
    r4 = register["rules"]["R4"]
    if not isinstance(configs, list) or not (r4["min"] <= len(configs) <= r4["max"]):
        n = len(configs) if isinstance(configs, list) else "not a list"
        c.flag("R4", f"datasetMetricConfigs holds {n}; the documented range is "
                     f"{r4['min']} to {r4['max']} items.")
        return c  # nothing further can be read reliably

    auto_set = set(register["rules"]["R1"]["documented_set"])
    judge_set = set(register["rules"]["R2"]["documented_set"])

    for idx, cfg in enumerate(configs):
        where = f"datasetMetricConfigs[{idx}]"
        metrics = cfg.get("metricNames", [])
        if not isinstance(metrics, list):
            metrics = []

        # ---- R5: metricNames bounds
        c.note("R5")
        r5 = register["rules"]["R5"]
        if not (r5["min"] <= len(metrics) <= r5["max"]):
            c.flag("R5", f"{where}.metricNames holds {len(metrics)}; the documented range is "
                         f"{r5['min']} to {r5['max']} items.")

        # ---- R1 / R2: metric name legality, conditioned on the evaluator
        if evaluator_present:
            # R2 checks only that a name is documented SOMEWHERE for a model evaluation job.
            # It deliberately does NOT reject the automated names when an evaluator is present:
            # AWS documents different sets for different configurations, which is not the same as
            # documenting them as mutually exclusive. See N5 in RULES.md. No warning is emitted
            # either - a warning would still imply this checker knows the answer.
            c.note("R2")
            documented_anywhere = judge_set | auto_set
            for m in metrics:
                if m not in documented_anywhere:
                    c.flag("R2", f"{where}.metricNames contains '{m}'. It is not among the metric "
                                 f"names AWS documents as valid for any model evaluation "
                                 f"configuration.")
        else:
            c.note("R1")
            for m in metrics:
                if m not in auto_set:
                    extra = ""
                    if m in judge_set:
                        extra = (" It is documented for model evaluation jobs that use a model as "
                                 "judge, which is a different configuration from this one.")
                    c.flag("R1", f"{where}.metricNames contains '{m}'. evaluatorModelConfig is "
                                 f"absent, and '{m}' is not among the metric names AWS documents as "
                                 f"valid for automated model evaluation jobs.{extra}")

        # ---- R3: reference data requirement
        needs_reference = bool({"Builtin.Accuracy", "Builtin.Robustness"} & set(metrics))
        if needs_reference and not evaluator_present and not dataset_is_builtin:
            c.note("R3")
            missing = [i for i, r in enumerate(records, start=1)
                       if not str(r.get("referenceResponse", "")).strip()]
            if missing:
                shown = ", ".join(str(i) for i in missing[:5])
                more = f" (and {len(missing) - 5} more)" if len(missing) > 5 else ""
                selected = sorted({"Builtin.Accuracy", "Builtin.Robustness"} & set(metrics))
                c.flag("R3", f"{where}.metricNames selects {', '.join(selected)} against a custom "
                             f"prompt dataset, and {len(missing)} of {len(records)} records carry no "
                             f"referenceResponse (record {shown}{more}). AWS documents "
                             f"referenceResponse as required for all accuracy and robustness "
                             f"evaluations in a custom prompt dataset.")

    # ---- R6: custom dataset size
    if not dataset_is_builtin:
        c.note("R6")
        r6 = register["rules"]["R6"]
        if len(records) > r6["max"]:
            c.flag("R6", f"the prompt dataset holds {len(records)} records; the documented maximum "
                         f"per evaluation job is {r6['max']}.")

    # ---- R7: bring-your-own inference responses
    if not dataset_is_builtin and any("modelResponses" in r for r in records):
        c.note("R7")
        ids, missing = set(), 0
        for r in records:
            mrs = r.get("modelResponses") or []
            if not mrs:
                missing += 1
                continue
            for mr in mrs:
                if mr.get("modelIdentifier"):
                    ids.add(mr["modelIdentifier"])
                else:
                    missing += 1
        if len(ids) > 1:
            c.flag("R7", f"the prompt dataset supplies inference responses under "
                         f"{len(ids)} different modelIdentifier values ({', '.join(sorted(ids))}). "
                         f"AWS documents one unique modelIdentifier per evaluation job.")
        if missing:
            c.flag("R7", f"{missing} record(s) supply no modelIdentifier. AWS documents that every "
                         f"prompt in the dataset must use the job's identifier.")

    return c


# --------------------------------------------------------------------------------------
# Output
# --------------------------------------------------------------------------------------

BANNER = "Episode 5 lab - measurement design checker"
LINE = "-" * 78


def main():
    ap = argparse.ArgumentParser(description="Validate a measurement design against documented "
                                             "Amazon Bedrock evaluation constraints.")
    ap.add_argument("--design", default=str(LAB / "my_design.json"))
    ap.add_argument("--rules", default=str(LAB / "rules_sources.json"))
    ap.add_argument("--quiet", action="store_true", help="findings only")
    args = ap.parse_args()

    register = load_json(Path(args.rules), "rule register")
    design = load_json(Path(args.design), "design file")

    if not args.quiet:
        print(LINE)
        print(BANNER)
        print(LINE)

    stray = unresolved_placeholders(design)
    if stray:
        lines = "\n".join(f"           {t} = {v}" for t, v in stray)
        fail_hard("TOOLING: the design file still holds scaffold placeholders:\n"
                  f"{lines}\n"
                  "         Replace each marked value with a decision before running the checker.\n"
                  "         This is a mechanical problem, not a finding about your measurement design.")

    dataset_file = (design.get("_lab") or {}).get("datasetFile")
    cfgs = design.get("evaluationConfig", {}).get("automated", {}).get("datasetMetricConfigs", [])
    ds_name = ""
    if cfgs and isinstance(cfgs[0], dict):
        ds_name = str((cfgs[0].get("dataset") or {}).get("name", ""))
    dataset_is_builtin = ds_name.startswith("Builtin.")

    records = []
    if not dataset_is_builtin:
        if not dataset_file:
            fail_hard("TOOLING: _lab.datasetFile names no file, and the dataset is not a built-in "
                      "one. The checker has nothing to read.")
        records = load_jsonl(LAB / dataset_file, f"prompt dataset '{dataset_file}'")

    auto = design.get("evaluationConfig", {}).get("automated", {})
    evaluator_present = auto.get("evaluatorModelConfig") not in (None, {}, [])

    if not args.quiet:
        print(f"design file        : {Path(args.design).name}")
        if evaluator_present:
            print("evaluator model    : configured")
            print("                     in a real CreateEvaluationJob request this is:")
            print('                     "evaluatorModelConfig": {"bedrockEvaluatorModels":')
            print('                       [{"modelIdentifier": "<a supported evaluator model id>"}]}')
        else:
            print("evaluator model    : not configured (evaluatorModelConfig is null)")
        print(f"prompt dataset     : {ds_name or dataset_file}"
              f"{' (built-in)' if dataset_is_builtin else f' ({len(records)} records)'}")
        print()

    c = run_rules(design, records, dataset_is_builtin, register)

    if c.findings:
        print(f"RESULT: NOT VALID under the documented constraints - "
              f"{len(c.findings)} finding(s)")
        print()
        for f in c.findings:
            print(f.render())
            print()
    else:
        print("RESULT: VALID under every constraint this checker enforces "
              f"({', '.join(sorted(set(c.checked)))}).")
        print()

    if not args.quiet:
        print(LINE)
        print("What this result does not establish:")
        for key in ("N1", "N2", "N3", "N4", "N5"):
            n = register["not_rules"][key]
            print(f"  {key}  {n['subject']}")
        print("  See RULES.md for why each is left unchecked.")
        print(LINE)

    sys.exit(1 if c.findings else 0)


if __name__ == "__main__":
    main()
