"""Tests for the comparability checker.

Two kinds of test live here.

  1. Behavioural: does the checker detect P1, P2 and P3 defects, and does it
     leave learner-owned judgements alone?
  2. Integrity: does this repository contain anything the lab promises it does
     not contain -- an answer key, a materiality label, a must-match list, a
     ranking path, a network dependency?

The integrity tests exist because the lab's central promise is about what the
tool CANNOT do. A promise like that has to be enforced, not asserted.

Standard library only. No network. No AWS.
"""

import ast
import copy
import io
import json
import os
import re
import sys
import unittest
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import check_review as C  # noqa: E402


SHIPPED_SKIP = ("__pycache__", "tests")


def shipped_files(exts):
    """Every file a learner receives, excluding this test suite.

    The integrity scans below look for words the lab promises not to contain.
    This file necessarily contains all of them as test data, so scanning it
    reports defects that are not there. Episode 5's lab hit this three times.
    """
    out = []
    for root, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SHIPPED_SKIP]
        for fn in sorted(files):
            if fn.endswith(exts):
                out.append(os.path.join(root, fn))
    return out


def code_only(path):
    """Source with all docstrings and comments removed.

    Prose about a forbidden concept is not an instance of it. Episode 5's lab
    learned this three times over: a scan that reads its own explanatory text
    reports defects that are not there.
    """
    with open(path) as f:
        src = f.read()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                node.body.pop(0)
    return ast.unparse(tree) if hasattr(ast, "unparse") else re.sub(r"#.*", "", src)


def sound_review(scenario_name):
    """A review that reasons correctly from what the scenario actually supplies.

    Built by READING the artifacts, not by looking anything up: the factual
    parts are derived, and the judgement parts are one defensible position
    among several. Nothing here is a reference answer.
    """
    s = C.load_scenario(scenario_name)
    held = sorted(s["a"].keys())
    observed, unknown, judgment = [], [], []
    for cond in sorted(C.CONDITIONS):
        gt = C.ground_truth(s, cond)
        if gt == "not_exposed":
            unknown.append({"condition": cond, "note": "not exposed by the artifacts supplied here"})
        else:
            ev = []
            for side in ("a", "b"):
                types = C.exposing_types(s[side], cond)
                if types:
                    ev.append("%s.%s" % (side, types[0]))
            observed.append({"condition": cond, "status": gt, "evidence": ev, "note": "read from the artifacts"})
    for cond in sorted(C.CONDITIONS):
        gt = C.ground_truth(s, cond)
        judgment.append({
            "condition": cond,
            "materiality": "cannot_classify" if gt == "not_exposed" else
                           ("material" if gt == "differs" else "immaterial"),
            "reasoning": "stated position for this claim"})
    return {"scenario": scenario_name,
            "comparison_claim_restated": "the claim under evaluation, restated",
            "claim_puts_in_scope": sorted(x["condition"] for x in s["claim"]["claim_scoped_conditions"]),
            "artifacts_i_hold": {"a": held, "b": sorted(s["b"].keys())},
            "observed": observed, "unknown": unknown, "judgment": judgment,
            "would_compare": "not_without_addressing",
            "before_comparing": "what I would retrieve or hold constant first"}


def kinds(findings):
    return sorted({f.kind for f in findings})


def powers(findings):
    return sorted({f.power for f in findings})


class TestCorrectFirstAttempt(unittest.TestCase):
    """No deliberate failure may be required to complete this lab."""

    def test_sound_review_passes_first_time_every_scenario(self):
        for name in ("scenario_01", "scenario_02", "scenario_03"):
            with self.subTest(name):
                f = C.check(C.load_scenario(name), sound_review(name))
                self.assertEqual(f, [], "%s: %s" % (name, [str(x) for x in f]))


class TestP1FactualVerification(unittest.TestCase):

    def test_asserting_same_when_artifacts_show_differs(self):
        r = sound_review("scenario_02")
        for e in r["observed"]:
            if e["condition"] == "inference_parameters":
                e["status"] = "same"
        f = C.check(C.load_scenario("scenario_02"), r)
        self.assertIn("FACTUAL_CONTRADICTION", kinds(f))
        self.assertIn("P1", powers(f))

    def test_asserting_differs_when_artifacts_show_same(self):
        r = sound_review("scenario_01")
        for e in r["observed"]:
            if e["condition"] == "dataset":
                e["status"] = "differs"
        f = C.check(C.load_scenario("scenario_01"), r)
        self.assertIn("FACTUAL_CONTRADICTION", kinds(f))

    def test_misstating_which_artifacts_are_held(self):
        r = sound_review("scenario_03")
        r["artifacts_i_hold"]["a"] = ["result_record", "job_summary", "job_definition"]
        f = C.check(C.load_scenario("scenario_03"), r)
        self.assertIn("FACTUAL_CONTRADICTION", kinds(f))


class TestP2EvidenceProvenance(unittest.TestCase):

    def test_claiming_to_know_a_condition_the_artifacts_do_not_expose(self):
        """The characteristic Episode 6 error, committed inside the lab."""
        r = sound_review("scenario_03")
        r["unknown"] = [u for u in r["unknown"] if u["condition"] != "inference_parameters"]
        r["observed"].append({"condition": "inference_parameters", "status": "same",
                              "evidence": [], "note": "asserted without support"})
        f = C.check(C.load_scenario("scenario_03"), r)
        self.assertIn("UNSUPPORTED_CITATION", kinds(f))
        self.assertIn("P2", powers(f))
        self.assertTrue(any("inference_parameters" in x.text for x in f))

    def test_citing_an_artifact_the_scenario_does_not_supply(self):
        r = sound_review("scenario_03")
        for e in r["observed"]:
            if e["condition"] == "model":
                e["evidence"] = ["a.job_definition", "b.job_definition"]
        f = C.check(C.load_scenario("scenario_03"), r)
        self.assertIn("UNSUPPORTED_CITATION", kinds(f))

    def test_citing_an_artifact_that_does_not_expose_that_condition(self):
        r = sound_review("scenario_01")
        for e in r["observed"]:
            if e["condition"] == "inference_parameters":
                e["evidence"] = ["a.result_record", "b.result_record"]
        f = C.check(C.load_scenario("scenario_01"), r)
        self.assertIn("UNSUPPORTED_CITATION", kinds(f))

    def test_recording_as_unknown_something_the_artifacts_do_expose(self):
        r = sound_review("scenario_01")
        r["observed"] = [e for e in r["observed"] if e["condition"] != "dataset"]
        r["unknown"].append({"condition": "dataset", "note": "wrongly recorded as unavailable"})
        f = C.check(C.load_scenario("scenario_01"), r)
        self.assertIn("UNSUPPORTED_CITATION", kinds(f))

    def test_judging_a_condition_never_established(self):
        r = sound_review("scenario_01")
        r["observed"] = [e for e in r["observed"] if e["condition"] != "model"]
        f = C.check(C.load_scenario("scenario_01"), r)
        self.assertTrue(any(x.power == "P2" and "model" in x.text for x in f))


class TestP3ClaimScope(unittest.TestCase):

    def test_calling_a_claim_scoped_difference_immaterial(self):
        r = sound_review("scenario_01")          # metric_name differs; the claim names it
        for e in r["judgment"]:
            if e["condition"] == "metric_name":
                e["materiality"] = "immaterial"
        f = C.check(C.load_scenario("scenario_01"), r)
        self.assertIn("CLAIM_SCOPE_CONFLICT", kinds(f))
        self.assertIn("P3", powers(f))

    def test_ignoring_a_condition_the_claim_names(self):
        r = sound_review("scenario_02")
        r["judgment"] = [e for e in r["judgment"] if e["condition"] != "dataset"]
        f = C.check(C.load_scenario("scenario_02"), r)
        self.assertIn("CLAIM_SCOPE_CONFLICT", kinds(f))

    def test_p3_does_not_fire_on_a_difference_the_claim_does_not_name(self):
        """scenario_02's inference_parameters difference is outside the claim's scope."""
        r = sound_review("scenario_02")
        for e in r["judgment"]:
            if e["condition"] == "inference_parameters":
                e["materiality"] = "immaterial"
        f = C.check(C.load_scenario("scenario_02"), r)
        self.assertEqual([], [x for x in f if x.power == "P3"], [str(x) for x in f])


class TestClaimIsLoadBearing(unittest.TestCase):
    """Ruling 9: a learner must not be able to finish without reading the claim."""

    def test_every_scenario_declares_scoped_conditions(self):
        for name in ("scenario_01", "scenario_02", "scenario_03"):
            claim = C.load_scenario(name)["claim"]
            self.assertTrue(claim.get("claim_scoped_conditions"), name)

    def test_every_scoped_quote_appears_verbatim_in_the_claim(self):
        """The scope list must be a reading of the claim, not free-floating metadata."""
        for name in ("scenario_01", "scenario_02", "scenario_03"):
            claim = C.load_scenario(name)["claim"]
            for s in claim["claim_scoped_conditions"]:
                self.assertIn(s["quote"], claim["claim"], "%s / %s" % (name, s["condition"]))

    def test_omitting_the_scope_reading_fails(self):
        for name in ("scenario_01", "scenario_02", "scenario_03"):
            with self.subTest(name):
                r = sound_review(name)
                r["claim_puts_in_scope"] = []
                f = C.check(C.load_scenario(name), r)
                self.assertIn("CLAIM_SCOPE_CONFLICT", kinds(f))

    def test_listing_every_condition_as_in_scope_fails(self):
        """A learner cannot pass by declaring everything in scope without reading."""
        for name in ("scenario_01", "scenario_02", "scenario_03"):
            with self.subTest(name):
                r = sound_review(name)
                r["claim_puts_in_scope"] = sorted(C.CONDITIONS)
                f = C.check(C.load_scenario(name), r)
                self.assertIn("CLAIM_SCOPE_CONFLICT", kinds(f))

    def test_scope_reading_is_required_as_a_field(self):
        r = sound_review("scenario_01")
        del r["claim_puts_in_scope"]
        f = C.check(C.load_scenario("scenario_01"), r)
        self.assertIn("INCOMPLETE_REVIEW", kinds(f))

    def test_ignoring_the_claim_entirely_fails_in_every_scenario(self):
        for name in ("scenario_01", "scenario_02", "scenario_03"):
            with self.subTest(name):
                r = sound_review(name)
                scoped = {s["condition"] for s in C.load_scenario(name)["claim"]["claim_scoped_conditions"]}
                r["judgment"] = [e for e in r["judgment"] if e["condition"] not in scoped]
                f = C.check(C.load_scenario(name), r)
                self.assertIn("CLAIM_SCOPE_CONFLICT", kinds(f))


class TestMultipleDefensibleJudgments(unittest.TestCase):
    """Ruling 15. Reasoning is still read; it is simply not graded."""

    def test_opposite_materiality_positions_both_pass(self):
        sc = C.load_scenario("scenario_02")
        for verdict in ("material", "immaterial", "cannot_classify"):
            with self.subTest(verdict):
                r = sound_review("scenario_02")
                for e in r["judgment"]:
                    if e["condition"] == "inference_parameters":
                        e["materiality"] = verdict
                        e["reasoning"] = "a defensible position for this claim"
                self.assertEqual([], C.check(sc, r))

    def test_every_would_compare_value_passes(self):
        sc = C.load_scenario("scenario_02")
        for v in C.WOULD_COMPARE_VALUES:
            with self.subTest(v):
                r = sound_review("scenario_02")
                r["would_compare"] = v
                self.assertEqual([], C.check(sc, r))

    def test_reasoning_is_not_ignored(self):
        """The judgement is unscored, but an empty review is still incomplete."""
        r = sound_review("scenario_02")
        r["judgment"][0]["reasoning"] = "   "
        f = C.check(C.load_scenario("scenario_02"), r)
        self.assertIn("INCOMPLETE_REVIEW", kinds(f))


class TestCaseCPrecision(unittest.TestCase):
    """Ruling 7. Detect the unsupported citation; prescribe nothing after it."""

    def test_all_materiality_labels_pass_for_a_correctly_recorded_unknown(self):
        sc = C.load_scenario("scenario_03")
        for verdict in C.MATERIALITY_VALUES:
            with self.subTest(verdict):
                r = sound_review("scenario_03")
                for e in r["judgment"]:
                    if e["condition"] == "inference_parameters":
                        e["materiality"] = verdict
                        e["reasoning"] = "a stated position"
                self.assertEqual([], C.check(sc, r), verdict)

    def test_all_would_compare_values_pass_in_the_unknown_scenario(self):
        sc = C.load_scenario("scenario_03")
        for v in C.WOULD_COMPARE_VALUES:
            with self.subTest(v):
                r = sound_review("scenario_03")
                r["would_compare"] = v
                self.assertEqual([], C.check(sc, r))


class TestNothingIsGraded(unittest.TestCase):

    def test_no_score_appears_in_any_output(self):
        out = io.StringIO()
        with redirect_stdout(out):
            C.run()
        text = out.getvalue().lower()
        for banned in ("score:", "points", "%)", "grade", "rating", "out of"):
            self.assertNotIn(banned, text, banned)

    def test_checker_prints_its_limitations_on_every_run(self):
        for args in (None, ["scenario_01"]):
            out = io.StringIO()
            with redirect_stdout(out):
                C.run(args)
            text = out.getvalue()
            self.assertIn("WHAT THIS CHECKER DID NOT CHECK", text)
            self.assertIn("does not determine whether two measurements are comparable", text)

    def test_no_verdict_vocabulary_is_emitted(self):
        """No forbidden verdict, and no warning standing in for one."""
        sc = C.load_scenario("scenario_01")
        r = sound_review("scenario_01")
        for e in r["judgment"]:
            if e["condition"] == "metric_name":
                e["materiality"] = "immaterial"
        texts = " ".join(x.text.lower() for x in C.check(sc, r))
        for banned in ("not comparable", "is comparable", "incompatible", "you should not compare",
                       "is material", "is immaterial", "warning", "severity", "recommend"):
            self.assertNotIn(banned, texts, banned)


class TestCheckerBoundaryIsClosed(unittest.TestCase):

    def test_only_three_powers_exist(self):
        sc = C.load_scenario("scenario_01")
        found = set()
        for name in ("scenario_01", "scenario_02", "scenario_03"):
            r = sound_review(name)
            r["observed"] = []
            r["unknown"] = []
            r["judgment"] = []
            found |= {f.power for f in C.check(C.load_scenario(name), r)}
        self.assertTrue(found <= {"P1", "P2", "P3", "structure"}, found)

    def test_source_declares_no_fourth_power(self):
        code = code_only(os.path.join(ROOT, "check_review.py"))
        self.assertEqual(sorted(set(re.findall(r"""['"](P[0-9])['"]""", code))),
                         ["P1", "P2", "P3"])

    def test_materiality_is_never_constrained_outside_claim_scope(self):
        """Every materiality label passes for every non-claim-scoped condition."""
        for name in ("scenario_01", "scenario_02", "scenario_03"):
            sc = C.load_scenario(name)
            scoped = {s["condition"] for s in sc["claim"]["claim_scoped_conditions"]}
            for cond in C.CONDITIONS:
                if cond in scoped:
                    continue
                for verdict in C.MATERIALITY_VALUES:
                    with self.subTest(scenario=name, condition=cond, verdict=verdict):
                        r = sound_review(name)
                        for e in r["judgment"]:
                            if e["condition"] == cond:
                                e["materiality"] = verdict
                                e["reasoning"] = "a stated position"
                        self.assertEqual([], C.check(sc, r))


class TestNoHiddenAnswerKey(unittest.TestCase):
    """Ruling 5. The lab promises no key exists. That has to be enforced."""

    # Exact key names. Substring matching would flag AWS's own documented
    # 'scores' member, which is data the artifact must carry, not a hidden key.
    FORBIDDEN_KEYS = frozenset((
        "materiality", "material", "immaterial", "expected", "answer", "solution",
        "correct", "verdict", "comparable", "comparability", "must_match", "mustmatch",
        "recommended", "winner", "rank", "ranking", "expected_materiality",
        "would_compare", "answer_key", "reference_review"))

    def _walk(self, obj, path, hits):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if C.is_doc_key(k):
                    continue
                if str(k).lower() in self.FORBIDDEN_KEYS:
                    hits.append("%s.%s" % (path, k))
                self._walk(v, "%s.%s" % (path, k), hits)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                self._walk(v, "%s[%d]" % (path, i), hits)

    def test_no_scenario_file_carries_a_judgement_bearing_key(self):
        hits = []
        for p in shipped_files((".json",)):
            if os.sep + "scenarios" + os.sep in p:
                with open(p) as f:
                    self._walk(json.load(f), os.path.basename(p), hits)
        self.assertEqual(hits, [], hits)

    def test_no_scenario_value_encodes_a_materiality_label(self):
        for p in shipped_files((".json",)):
            if os.sep + "scenarios" + os.sep not in p:
                continue
            fn = os.path.basename(p)
            if True:
                with open(p) as f:
                    blob = json.load(f)
                text = json.dumps({k: v for k, v in blob.items() if not C.is_doc_key(k)}).lower()
                # Whole words only: AWS's own "QuestionAndAnswer" task type and
                # "scores" member are documented data, not judgement labels.
                for term in ("material", "immaterial", "cannot_classify", "comparable",
                             "would_compare", "expected", "answer", "verdict"):
                    self.assertIsNone(re.search(r"\b%s\b" % term, text),
                                      "%s in %s" % (term, fn))

    def test_no_reference_solution_file_exists(self):
        bad = [p for p in shipped_files((".py", ".json", ".md"))
               if any(t in os.path.basename(p).lower()
                      for t in ("solution", "answer", "expected", "reference_review",
                                "model_answer", "key."))]
        self.assertEqual(bad, [], bad)

    def test_shipped_reviews_are_pristine_scaffolds(self):
        for name in ("scenario_01", "scenario_02", "scenario_03"):
            with open(os.path.join(ROOT, "reviews", "%s_review.json" % name)) as f:
                self.assertTrue(C.has_placeholder(json.load(f)), name)

    def test_checker_code_holds_no_must_match_list(self):
        code = code_only(os.path.join(ROOT, "check_review.py")).lower()
        for term in ("must_match", "mustmatch", "required_fields", "comparability_score",
                     "materiality_score", "expected_materiality", "answer_key"):
            self.assertNotIn(term, code, term)


class TestBoundaries(unittest.TestCase):

    def _repo_text(self, include_prose=True):
        chunks = []
        for p in shipped_files((".py", ".json")):
            if p.endswith(".py"):
                chunks.append(code_only(p))
            elif include_prose:
                with open(p) as f:
                    chunks.append(f.read())
        return "\n".join(chunks).lower()

    def test_no_episode_7_selection_path(self):
        """No winner, ranking or recommendation anywhere in code or scenarios."""
        text = self._repo_text()
        for term in ("winner", "leaderboard", "ranking", "rank_models", "best_model",
                     "recommended_model", "deploy"):
            self.assertNotIn(term, text, term)

    def test_review_schema_has_no_field_for_a_winner(self):
        with open(os.path.join(ROOT, "reviews", "scenario_01_review.json")) as f:
            keys = [k for k in json.load(f) if not C.is_doc_key(k)]
        for term in ("winner", "rank", "preferred", "recommend", "deploy", "cost"):
            self.assertFalse(any(term in k.lower() for k in keys), term)

    def test_no_episode_4_sufficiency_vocabulary_in_code(self):
        text = self._repo_text(include_prose=False)
        for term in ("sufficient", "good_enough", "justify", "threshold", "quality_gate"):
            self.assertNotIn(term, text, term)

    def test_no_episode_5_checker_is_imported(self):
        code = code_only(os.path.join(ROOT, "check_review.py"))
        for term in ("check_design", "aip_c01_labs", "episode_05", "episode-05"):
            self.assertNotIn(term, code.lower(), term)


class TestNoAwsOrNetworkDependency(unittest.TestCase):

    def test_standard_library_only(self):
        allowed = {"ast", "copy", "io", "json", "os", "re", "sys", "unittest", "contextlib"}
        for p in shipped_files((".py",)) + [os.path.join(HERE, "test_checker.py")]:
                with open(p) as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for a in node.names:
                            base = a.name.split(".")[0]
                            self.assertTrue(base in allowed or base == "check_review", a.name)
                    elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                        self.assertIn(node.module.split(".")[0], allowed, node.module)

    def test_no_network_or_aws_client_calls_in_code(self):
        for p in shipped_files((".py",)):
            code = code_only(p).lower()
            for term in ("boto3", "botocore", "urllib", "requests", "http.client",
                         "socket", "subprocess", "os.system"):
                self.assertNotIn(term, code, "%s in %s" % (term, p))

    def test_no_credentials_or_real_identifiers(self):
        for p in shipped_files((".py", ".json", ".md")):
            with open(p) as f:
                text = f.read()
            self.assertIsNone(re.search(r"AKIA[0-9A-Z]{16}", text), p)
            self.assertIsNone(re.search(r"aws_secret_access_key", text, re.I), p)
            for acct in re.findall(r"\b\d{12}\b", text):
                self.assertEqual(acct, "111122223333", "%s in %s" % (acct, p))


class TestSyntheticDataIsLabelled(unittest.TestCase):
    """Ruling 19: synthetic values must never read as observed AWS results."""

    def test_every_scenario_artifact_declares_itself_synthetic(self):
        for p in shipped_files((".json",)):
            fn = os.path.basename(p)
            if os.sep + "scenarios" + os.sep not in p or fn == "claim.json":
                continue
            if True:
                with open(p) as f:
                    blob = json.load(f)
                about = blob.get("_about", "").lower()
                self.assertIn("synthetic", about, fn)
                self.assertIn("not", about, fn)


class TestRegressionPlaceholderScan(unittest.TestCase):
    """Regression: a documentation key may quote the placeholder marker safely.

    Episode 5's lab shipped the opposite behaviour into its student path and
    every unit test passed regardless. This asserts the fix directly.
    """

    def test_documentation_keys_are_skipped(self):
        self.assertFalse(C.has_placeholder({"_about": "replace every <FILL IN ...> marker",
                                            "field": "authored"}))

    def test_real_placeholders_are_still_detected(self):
        self.assertTrue(C.has_placeholder({"_about": "notes", "field": "<FILL IN: something>"}))

    def test_nested_placeholders_are_detected(self):
        self.assertTrue(C.has_placeholder({"a": [{"b": "<FILL IN: x>"}]}))


class TestEvaluatorExposureRegression(unittest.TestCase):
    """Regression: an absent evaluatorModelConfig is a fact, not a gap.

    Reading it as "not exposed" fired a provenance finding at a learner who
    correctly observed that neither job configured an evaluator model.
    """

    def test_definition_without_evaluator_config_establishes_the_condition(self):
        self.assertEqual(C.ground_truth(C.load_scenario("scenario_01"), "evaluator_model"), "same")

    def test_summary_alone_does_not_establish_it(self):
        self.assertEqual(C.ground_truth(C.load_scenario("scenario_03"), "evaluator_model"),
                         "not_exposed")


if __name__ == "__main__":
    unittest.main(verbosity=2)
