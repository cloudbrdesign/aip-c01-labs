#!/usr/bin/env python3
"""
Episode 5 lab - checker tests. Standard library only:  python3 tests/test_checker.py

Three groups:
  Functional    - the enforced rules fire when they should and stay quiet when they should not
  Pedagogical   - the checker stays a constraint validator: no recommendations, no result values,
                  more than one design passes
  Boundary      - nothing from a later episode leaks into the learner-facing surface
"""

import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(LAB / "scripts"))

import check_design as cd  # noqa: E402

REGISTER = json.loads((LAB / "rules_sources.json").read_text(encoding="utf-8"))
WITH_REF = [json.loads(l) for l in (LAB / "prompts_with_reference.jsonl").read_text().splitlines() if l.strip()]
NO_REF = [json.loads(l) for l in (LAB / "prompts_no_reference.jsonl").read_text().splitlines() if l.strip()]


def design(metrics, evaluator=None, task="Summarization", ds="handover-summaries", n_cfg=1):
    cfg = {"taskType": task, "dataset": {"name": ds}, "metricNames": list(metrics)}
    return {"evaluationConfig": {"automated": {
        "datasetMetricConfigs": [dict(cfg) for _ in range(n_cfg)],
        "evaluatorModelConfig": evaluator}},
        "_lab": {"datasetFile": "x.jsonl"}}


def run(d, records, builtin=False):
    return cd.run_rules(d, records, builtin, REGISTER)


def ids(c):
    return sorted({f.rule_id for f in c.findings})


# ----------------------------------------------------------------------------- functional
class Functional(unittest.TestCase):

    def test_valid_automatic_with_reference_passes(self):
        c = run(design(["Builtin.Accuracy"]), WITH_REF)
        self.assertEqual(c.findings, [], msg=[f.detail for f in c.findings])

    def test_valid_judge_without_reference_passes(self):
        c = run(design(["Builtin.Correctness"], evaluator="USE_JUDGE_MODEL"), NO_REF)
        self.assertEqual(c.findings, [], msg=[f.detail for f in c.findings])

    def test_R1_fires_judge_metric_without_evaluator(self):
        """The lab's primary predicted error."""
        c = run(design(["Builtin.Correctness", "Builtin.Faithfulness"]), NO_REF)
        self.assertIn("R1", ids(c))
        self.assertEqual(len([f for f in c.findings if f.rule_id == "R1"]), 2)

    def test_R1_says_the_metric_belongs_to_a_different_configuration(self):
        c = run(design(["Builtin.Faithfulness"]), NO_REF)
        d = [f.detail for f in c.findings if f.rule_id == "R1"][0]
        self.assertIn("model as judge", d)

    def test_R2_fires_automatic_metric_with_evaluator(self):
        c = run(design(["Builtin.Accuracy"], evaluator="USE_JUDGE_MODEL"), NO_REF)
        self.assertIn("R2", ids(c))

    def test_R3_fires_accuracy_on_dataset_without_reference(self):
        """The lab's second predicted error."""
        c = run(design(["Builtin.Accuracy"]), NO_REF)
        self.assertIn("R3", ids(c))

    def test_R3_quiet_when_references_present(self):
        self.assertNotIn("R3", ids(run(design(["Builtin.Robustness"]), WITH_REF)))

    def test_R3_quiet_for_builtin_dataset(self):
        d = design(["Builtin.Accuracy"], ds="Builtin.T-REx")
        self.assertNotIn("R3", ids(run(d, [], builtin=True)))

    def test_R3_quiet_when_metric_needs_no_reference(self):
        self.assertNotIn("R3", ids(run(design(["Builtin.Toxicity"]), NO_REF)))

    def test_R4_bounds(self):
        self.assertIn("R4", ids(run(design(["Builtin.Toxicity"], n_cfg=6), NO_REF)))
        self.assertIn("R4", ids(run(design(["Builtin.Toxicity"], n_cfg=0), NO_REF)))
        self.assertNotIn("R4", ids(run(design(["Builtin.Toxicity"], n_cfg=5), NO_REF)))

    def test_R5_bounds(self):
        self.assertIn("R5", ids(run(design([]), NO_REF)))
        self.assertIn("R5", ids(run(design(["Builtin.Toxicity"] * 26), NO_REF)))

    def test_R6_dataset_size(self):
        self.assertIn("R6", ids(run(design(["Builtin.Toxicity"]), NO_REF * 101)))

    def test_R7_multiple_model_identifiers(self):
        recs = [{"prompt": "p", "modelResponses": [{"response": "r", "modelIdentifier": m}]}
                for m in ("a", "b")]
        self.assertIn("R7", ids(run(design(["Builtin.Toxicity"]), recs)))

    def test_R7_missing_model_identifier(self):
        recs = [{"prompt": "p", "modelResponses": [{"response": "r"}]}]
        self.assertIn("R7", ids(run(design(["Builtin.Toxicity"]), recs)))

    def test_every_documented_judge_metric_is_accepted(self):
        js = REGISTER["rules"]["R2"]["documented_set"]
        c = run(design(js, evaluator="USE_JUDGE_MODEL"), NO_REF)
        self.assertEqual([f for f in c.findings if f.rule_id == "R2"], [])

    def test_every_finding_carries_a_resolvable_source(self):
        c = run(design(["Builtin.Correctness", "Builtin.Accuracy"]), NO_REF)
        self.assertTrue(c.findings)
        for f in c.findings:
            self.assertIn(f.source_id, REGISTER["sources"])
            self.assertTrue(f.source_url.startswith("https://docs.aws.amazon.com/"))


# --------------------------------------------------------------------------- non-rules
class NonRulesNotEnforced(unittest.TestCase):
    """N1-N4 must never be silently enforced."""

    def test_N1_taskType_value_never_rejected(self):
        for t in ("General", "Summarization", "Custom", "anything-at-all"):
            c = run(design(["Builtin.Toxicity"], task=t), NO_REF)
            self.assertEqual(c.findings, [], msg=f"taskType {t!r} was rejected")

    def test_N2_dataset_name_casing_never_rejected(self):
        for n in ("Builtin.BOLD", "Builtin.Bold", "my-dataset"):
            builtin = n.startswith("Builtin.")
            c = run(design(["Builtin.Toxicity"], ds=n), [] if builtin else NO_REF, builtin)
            self.assertEqual(c.findings, [], msg=f"dataset name {n!r} was rejected")

    def test_N3_task_dataset_pairing_never_rejected(self):
        d = design(["Builtin.Accuracy"], task="Classification", ds="Builtin.T-REx")
        self.assertEqual(run(d, [], builtin=True).findings, [])

    def test_N4_appropriateness_never_judged(self):
        """A legal-but-arguably-poor design must pass; the checker cannot judge fit."""
        d = design(["Builtin.Toxicity"], task="Summarization")
        self.assertEqual(run(d, NO_REF).findings, [])


# ------------------------------------------------------------------------- pedagogical
def output_for(d, records, builtin=False):
    buf = io.StringIO()
    c = run(d, records, builtin)
    with redirect_stdout(buf):
        for f in c.findings:
            print(f.render())
    return buf.getvalue()


class Pedagogical(unittest.TestCase):

    PRESCRIPTIVE = [
        r"\byou should\b", r"\bplease use\b", r"\btry using\b", r"\bthe best\b",
        r"\brecommend", r"\bfix this by\b", r"\binstead,? (?:use|choose|select)\b",
        r"\bwe suggest\b", r"\byou need to (?:use|choose|select|add)\b",
    ]

    def all_findings_text(self):
        cases = [
            (design(["Builtin.Correctness"]), NO_REF, False),
            (design(["Builtin.Accuracy"]), NO_REF, False),
            (design(["Builtin.Accuracy"], evaluator="USE_JUDGE_MODEL"), NO_REF, False),
            (design(["Builtin.Toxicity"], n_cfg=6), NO_REF, False),
            (design([]), NO_REF, False),
        ]
        return "\n".join(output_for(*c) for c in cases)

    def test_checker_never_prescribes(self):
        text = self.all_findings_text().lower()
        for pat in self.PRESCRIPTIVE:
            self.assertIsNone(re.search(pat, text), msg=f"prescriptive language matched {pat!r}")

    def test_no_result_value_language_anywhere(self):
        """No score exists anywhere in this lab."""
        source = (LAB / "scripts" / "check_design.py").read_text(encoding="utf-8").lower()
        for banned in ("score", "grade", "rating", "percentile", "benchmark result"):
            self.assertNotIn(banned, source, msg=f"{banned!r} appears in the checker")
        self.assertNotIn("score", self.all_findings_text().lower())

    def test_more_than_one_design_passes(self):
        passing = [
            (design(["Builtin.Accuracy"]), WITH_REF, False),
            (design(["Builtin.Toxicity"]), NO_REF, False),
            (design(["Builtin.Accuracy", "Builtin.Robustness"]), WITH_REF, False),
            (design(["Builtin.Correctness"], evaluator="USE_JUDGE_MODEL"), NO_REF, False),
            (design(["Builtin.Faithfulness", "Builtin.Relevance"], evaluator="USE_JUDGE_MODEL"), NO_REF, False),
            (design(["Builtin.Correctness", "Builtin.Completeness"], evaluator="USE_JUDGE_MODEL"), WITH_REF, False),
            (design(["Builtin.Accuracy"], ds="Builtin.T-REx"), [], True),
        ]
        clean = [i for i, (d, r, b) in enumerate(passing) if not run(d, r, b).findings]
        self.assertGreaterEqual(len(clean), 6,
                                msg="the lab must not encode a single canonical answer")

    def test_syntax_failure_is_labelled_tooling(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
            fh.write("{ not json ")
            broken = fh.name
        proc = subprocess.run(
            [sys.executable, str(LAB / "scripts" / "check_design.py"), "--design", broken],
            capture_output=True, text=True)
        self.assertIn("TOOLING", proc.stdout)
        self.assertIn("not a finding about your measurement design", proc.stdout)

    @staticmethod
    def _scaffold_is_pristine():
        d = json.loads((LAB / "my_design.json").read_text(encoding="utf-8"))
        body = json.dumps({k: v for k, v in d.items() if k != "_README"})
        return "<CHOICE" in body

    def test_documentation_keys_are_not_scanned_for_placeholders(self):
        if not self._scaffold_is_pristine():
            self.skipTest("my_design.json has been edited - expected once you have done the lab. "
                          "Run `git checkout my_design.json` to restore the scaffold.")
        """Regression: _README explains the <CHOICE ...> convention and so contains the marker.
        Scanning it made the scaffold permanently unresolvable - no learner could get past it."""
        d = json.loads((LAB / "my_design.json").read_text(encoding="utf-8"))
        self.assertTrue(any("<CHOICE" in s for s in d["_README"]),
                        "_README no longer documents the convention; this test is now moot")
        for choice in ("<CHOICE 1", "<CHOICE 2", "<CHOICE 3", "<CHOICE 4", "<CHOICE 5"):
            self.assertTrue(any(choice in json.dumps(v) for k, v in d.items() if k != "_README"),
                            f"{choice} is not in an editable position")
        resolved = json.loads(json.dumps(d))
        a = resolved["evaluationConfig"]["automated"]
        a["datasetMetricConfigs"][0]["taskType"] = "Summarization"
        a["datasetMetricConfigs"][0]["dataset"]["name"] = "ds"
        a["datasetMetricConfigs"][0]["metricNames"] = ["Builtin.Toxicity"]
        a["evaluatorModelConfig"] = None
        resolved["_lab"]["datasetFile"] = "prompts_no_reference.jsonl"
        self.assertEqual(cd.unresolved_placeholders(resolved), [],
                         "a fully-resolved design still reports placeholders")

    def test_unresolved_placeholder_is_tooling_not_a_finding(self):
        if not self._scaffold_is_pristine():
            self.skipTest("my_design.json has been edited - expected once you have done the lab. "
                          "Run `git checkout my_design.json` to restore the scaffold.")
        proc = subprocess.run(
            [sys.executable, str(LAB / "scripts" / "check_design.py"),
             "--design", str(LAB / "my_design.json")],
            capture_output=True, text=True)
        self.assertIn("TOOLING", proc.stdout)
        self.assertIn("placeholder", proc.stdout.lower())

    def test_run_reports_what_it_did_not_establish(self):
        proc = subprocess.run(
            [sys.executable, str(LAB / "scripts" / "check_design.py"),
             "--design", str(LAB / "evidence" / "open-after-step-5" / "one_valid_design.json")],
            capture_output=True, text=True)
        self.assertIn("What this result does not establish", proc.stdout)
        for n in ("N1", "N2", "N3", "N4"):
            self.assertIn(n, proc.stdout)


# ----------------------------------------------------------------------------- boundary
class Boundary(unittest.TestCase):
    """Nothing owned by a later episode may appear on the learner-facing surface."""

    LEARNER_FACING = [
        "README.md", "SCENARIO.md", "LAB_GUIDE.md", "RULES.md", "TROUBLESHOOTING.md",
        "EVIDENCE_TEMPLATE.md", "my_design.json",
        "scripts/check_design.py", "scripts/preflight.py",
        "evidence/README.md",
        "evidence/open-after-step-5/README.md",
        "evidence/open-after-step-5/WHY_THIS_IS_LEGAL.md",
        "evidence/open-after-step-5/one_valid_design.json",
    ]

    FORBIDDEN = [
        r"\bthreshold\b", r"\bquality gate\b", r"\bregression test", r"\bcontinuous evaluation\b",
        r"\ba/b test", r"\bcanary\b", r"\bdegradation curve\b",
        r"\bwhich model (?:is better|to (?:pick|choose))\b", r"\bmodel ranking\b",
        r"\bcost[- ]performance\b", r"\bprice[- ]to[- ]performance\b",
        r"\bgood enough\b", r"\bsufficient evidence\b", r"\bdeploy(?:ment)? decision\b",
        r"\bjudge prompt\b", r"\bposition bias\b", r"\bpairwise\b", r"\bcalibrat",
        r"\bscore", r"\bgrade[sd]?\b", r"\brating\b",
    ]

    def test_no_deferred_concept_on_learner_surface(self):
        for rel in self.LEARNER_FACING:
            p = LAB / rel
            if not p.is_file():
                continue
            text = p.read_text(encoding="utf-8").lower()
            for pat in self.FORBIDDEN:
                self.assertIsNone(re.search(pat, text),
                                  msg=f"{rel} matches deferred-concept pattern {pat!r}")

    # Real code tokens, not prose. A docstring may say "No AWS credentials"; what must not
    # exist is anything that could reach the network or read an AWS identity.
    NETWORK_OR_IDENTITY = (
        "boto3", "botocore", "urllib", "requests", "http.client", "httpx", "socket",
        "AWS_ACCESS_KEY", "AWS_SECRET", "AWS_SESSION_TOKEN", "AWS_PROFILE",
        "get_caller_identity", ".aws/credentials", ".aws/config", "os.environ",
    )

    @staticmethod
    def _code_only(path):
        """Source with docstrings and comments stripped, so prose cannot trip the scan."""
        import ast
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                if (node.body and isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                        and isinstance(node.body[0].value.value, str)):
                    node.body.pop(0)
        return ast.unparse(tree)

    def test_no_aws_call_surface_anywhere(self):
        for p in LAB.rglob("*.py"):
            if p.resolve() == Path(__file__).resolve():
                continue  # this file names the banned tokens in order to ban them
            code = self._code_only(p)
            for banned in self.NETWORK_OR_IDENTITY:
                self.assertNotIn(banned, code, msg=f"{p.name} contains code referencing {banned!r}")

    def test_only_stdlib_imports(self):
        """Whitelist every module the lab may import."""
        import ast
        allowed = {"argparse", "json", "sys", "pathlib", "io", "re", "subprocess",
                   "tempfile", "unittest", "contextlib", "check_design", "ast"}
        for p in LAB.rglob("*.py"):
            for node in ast.walk(ast.parse(p.read_text(encoding="utf-8"))):
                mods = []
                if isinstance(node, ast.Import):
                    mods = [a.name.split(".")[0] for a in node.names]
                elif isinstance(node, ast.ImportFrom) and node.module:
                    mods = [node.module.split(".")[0]]
                for m in mods:
                    self.assertIn(m, allowed, msg=f"{p.name} imports {m!r}")

    def test_stdlib_only(self):
        self.assertFalse((LAB / "requirements.txt").exists(),
                         "this lab has no third-party dependencies")


if __name__ == "__main__":
    unittest.main(verbosity=2)
