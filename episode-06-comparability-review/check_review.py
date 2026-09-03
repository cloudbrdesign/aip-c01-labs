#!/usr/bin/env python3
"""Review checker.

It validates limited properties of YOUR REVIEW. It does not validate comparability.

WHAT THIS TOOL DOES

It verifies facts. Three classes of them, and nothing else:

  P1  FACTUAL VERIFICATION
      Does a statement you made about sameness or difference agree with the
      artifacts this scenario supplied?

  P2  EVIDENCE-PROVENANCE VERIFICATION
      Does the artifact you are holding actually expose the condition your
      reasoning claims to know about?

  P3  CLAIM-SCOPE CONSISTENCY
      Where the comparison claim itself names a condition, does your reasoning
      contradict or ignore the scope the claim declared?

WHAT THIS TOOL DOES NOT DO

It does not decide whether two measurements are comparable, and it does not
decide which observed differences are material. There is no answer key in this
repository for those questions, because no such key exists to be written. AWS
documents no list of fields that must match for two evaluation results to be
comparable, and this lab does not invent one.

Materiality and your would-compare conclusion are yours. They are read for
structural completeness and, where the claim itself settles the point, for
internal consistency. They are never scored, ranked, or compared against a
preferred answer.

PASS means: this review artifact passed the checker's limited mechanical checks.
PASS does not mean: your comparison judgement is correct.

Python 3.9+. Standard library only. No network. No AWS account. No credentials.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SCENARIOS = os.path.join(HERE, "scenarios")
REVIEWS = os.path.join(HERE, "reviews")

# Keys whose job is to EXPLAIN the file they live in. The placeholder scan must
# skip them: they legitimately contain the placeholder marker as example text.
# (Episode 5's lab shipped this defect to its own student path and every unit
# test passed anyway. It is fixed here from the first commit.)
# Any key whose name starts with an underscore is documentation. Naming them
# explicitly was the narrower fix; skipping the whole prefix is the robust one,
# because a note added later may legitimately quote the marker as an example.
def is_doc_key(k):
    return isinstance(k, str) and k.startswith("_")

PLACEHOLDER = re.compile(r"<FILL IN[^>]*>")

ARTIFACT_TYPES = ("result_record", "job_summary", "job_definition")

# Documented S3 output key template for an automatic model evaluation job.
# See SOURCE_MAP.json -> result_record.s3_key.
S3_KEY = re.compile(
    r"^s3://[^/]+/(?:.*/)?(?P<job_name>[^/]+)/(?P<job_uuid>[^/]+)/models/(?P<model_id>.+?)"
    r"/taskTypes/(?P<task_type>[^/]+)/datasets/(?P<dataset>[^/]+)/[^/]+$"
)

MATERIALITY_VALUES = ("material", "immaterial", "cannot_classify")
WOULD_COMPARE_VALUES = ("yes", "no", "not_without_addressing")
STATUS_VALUES = ("same", "differs")


# --------------------------------------------------------------------------
# Conditions.
#
# A condition is something an engineer might want to know about how a
# measurement was produced. This table records ONLY where each condition is
# exposed and how to read it. It records nothing about whether a condition
# matters. Every entry traces to SOURCE_MAP.json.
# --------------------------------------------------------------------------

def _s3_part(art, part):
    m = S3_KEY.match(art.get("s3_key", ""))
    return m.group(part) if m else None


def _models_from_definition(art):
    out = []
    for m in art.get("inferenceConfig", {}).get("models", []):
        bm = m.get("bedrockModel")
        if bm:
            out.append(bm.get("modelIdentifier"))
        else:
            out.append(m.get("precomputedInferenceSource", {}).get("inferenceSourceIdentifier"))
    return out


def _dmc(art):
    return art.get("evaluationConfig", {}).get("automated", {}).get("datasetMetricConfigs", [])


def _inference_params(art):
    vals = []
    for m in art.get("inferenceConfig", {}).get("models", []):
        raw = m.get("bedrockModel", {}).get("inferenceParams")
        if raw is None:
            vals.append(None)
        else:
            try:
                vals.append(json.loads(raw))
            except (ValueError, TypeError):
                vals.append(raw)
    return vals


# A returned job definition that carries no evaluatorModelConfig establishes that
# no evaluator model was configured. That is a fact, not a gap, so it must not be
# read as "not exposed" -- doing so would fire a provenance finding at a learner
# who correctly observed that neither job configured one. A job SUMMARY carrying
# an empty evaluatorModelIdentifiers list is genuinely ambiguous between "none"
# and "none reported", so the summary is deliberately NOT read as establishing it.
NONE_CONFIGURED = "<no evaluator model configured>"


def _evaluator_from_definition(art):
    auto = art.get("evaluationConfig", {}).get("automated", {})
    cfg = auto.get("evaluatorModelConfig")
    if cfg is None:
        return [NONE_CONFIGURED]
    return [m.get("modelIdentifier") for m in cfg.get("bedrockEvaluatorModels", [])]


# condition -> ordered list of (artifact_type, reader). First artifact type that
# is actually supplied wins. Order is fidelity, not a retrieval procedure: these
# are places a fact is documented, not steps to perform.
CONDITIONS = {
    "model": [
        ("job_definition", _models_from_definition),
        ("job_summary", lambda a: a.get("inferenceConfigSummary", {})
                                   .get("modelConfigSummary", {})
                                   .get("bedrockModelIdentifiers")),
        ("result_record", lambda a: [_s3_part(a, "model_id")]),
    ],
    "task_type": [
        ("job_definition", lambda a: sorted({d.get("taskType") for d in _dmc(a)})),
        ("job_summary", lambda a: sorted(a.get("evaluationTaskTypes", []))),
        ("result_record", lambda a: [_s3_part(a, "task_type")]),
    ],
    "dataset": [
        ("job_definition", lambda a: sorted({d.get("dataset", {}).get("name") for d in _dmc(a)})),
        ("result_record", lambda a: [_s3_part(a, "dataset")]),
    ],
    "metric_name": [
        ("job_definition", lambda a: sorted({m for d in _dmc(a) for m in d.get("metricNames", [])})),
        ("result_record", lambda a: sorted({s.get("metricName")
                                            for r in a.get("records", [])
                                            for s in r.get("automatedEvaluationResult", {})
                                                       .get("scores", [])})),
    ],
    "evaluator_model": [
        ("job_definition", _evaluator_from_definition),
        ("job_summary", lambda a: sorted(a.get("evaluatorModelIdentifiers", []))),
    ],
    "inference_parameters": [
        ("job_definition", _inference_params),
    ],
    "reference_response_present": [
        ("result_record", lambda a: sorted({"referenceResponse" in r.get("inputRecord", {})
                                            for r in a.get("records", [])})),
    ],
}

CONDITION_HELP = {
    "model": "which model produced the responses",
    "task_type": "the task type the job declared",
    "dataset": "the prompt dataset the job ran against",
    "metric_name": "the metric name the job selected",
    "evaluator_model": "the evaluator model, where one is configured",
    "inference_parameters": "the inference parameters the model was invoked with",
    "reference_response_present": "whether the prompt records carry a reference response",
}


# --------------------------------------------------------------------------

class Finding:
    def __init__(self, kind, power, text):
        self.kind, self.power, self.text = kind, power, text

    def __str__(self):
        return "  [%s / %s] %s" % (self.kind, self.power, self.text)


def exposure(artifacts, condition):
    """(exposed, value, artifact_type) using ONLY the artifacts supplied."""
    for art_type, reader in CONDITIONS[condition]:
        art = artifacts.get(art_type)
        if art is None:
            continue
        val = reader(art)
        if val is None or (isinstance(val, list) and (not val or all(v is None for v in val))):
            continue
        return True, val, art_type
    return False, None, None


def exposing_types(artifacts, condition):
    out = []
    for art_type, reader in CONDITIONS[condition]:
        art = artifacts.get(art_type)
        if art is None:
            continue
        val = reader(art)
        if val is None or (isinstance(val, list) and (not val or all(v is None for v in val))):
            continue
        out.append(art_type)
    return out


def ground_truth(scenario, condition):
    """'same' | 'differs' | 'not_exposed' -- from the supplied artifacts only."""
    ea, va, _ = exposure(scenario["a"], condition)
    eb, vb, _ = exposure(scenario["b"], condition)
    if not (ea and eb):
        return "not_exposed"
    return "same" if va == vb else "differs"


def load_scenario(name):
    d = os.path.join(SCENARIOS, name)
    with open(os.path.join(d, "claim.json")) as f:
        claim = json.load(f)
    sides = {}
    for side in ("a", "b"):
        arts = {}
        for t in ARTIFACT_TYPES:
            p = os.path.join(d, "%s_%s.json" % (side, t))
            if os.path.exists(p):
                with open(p) as f:
                    arts[t] = json.load(f)
        sides[side] = arts
    return {"name": name, "claim": claim, "a": sides["a"], "b": sides["b"]}


def has_placeholder(obj):
    if isinstance(obj, dict):
        return any(has_placeholder(v) for k, v in obj.items() if not is_doc_key(k))
    if isinstance(obj, list):
        return any(has_placeholder(v) for v in obj)
    if isinstance(obj, str):
        return bool(PLACEHOLDER.search(obj))
    return False


# --------------------------------------------------------------------------
# The three powers. This list is closed. Nothing else may be added to it.
# --------------------------------------------------------------------------

def check(scenario, review):
    f = []
    claim = scenario["claim"]
    scoped = {s["condition"]: s for s in claim.get("claim_scoped_conditions", [])}

    # --- structural completeness (not a power; the artifact must be readable)
    required = ("comparison_claim_restated", "claim_puts_in_scope", "artifacts_i_hold",
                "observed", "unknown", "judgment", "would_compare", "before_comparing")
    for k in required:
        if k not in review:
            f.append(Finding("INCOMPLETE_REVIEW", "structure", "Your review has no '%s' section." % k))
    if f:
        return f

    if review.get("would_compare") not in WOULD_COMPARE_VALUES:
        f.append(Finding("INCOMPLETE_REVIEW", "structure",
                         "'would_compare' must be one of %s. It is not scored -- "
                         "the checker only needs it to be a stated position."
                         % ", ".join(WOULD_COMPARE_VALUES)))
    if not str(review.get("comparison_claim_restated", "")).strip():
        f.append(Finding("INCOMPLETE_REVIEW", "structure", "'comparison_claim_restated' is empty."))
    if not str(review.get("before_comparing", "")).strip():
        f.append(Finding("INCOMPLETE_REVIEW", "structure", "'before_comparing' is empty."))

    # --- artifacts_i_hold, and P1 on it
    held = review.get("artifacts_i_hold", {})
    for side in ("a", "b"):
        stated = sorted(held.get(side, []) or [])
        actual = sorted(scenario[side].keys())
        if stated != actual:
            f.append(Finding("FACTUAL_CONTRADICTION", "P1",
                             "Your review says measurement %s supplies %s. This scenario supplies %s."
                             % (side.upper(), stated or "nothing", actual)))

    # --- P1 / P2 over 'observed'
    seen = set()
    for e in review.get("observed", []):
        c, st = e.get("condition"), e.get("status")
        if c not in CONDITIONS:
            f.append(Finding("UNKNOWN_CONDITION", "structure",
                             "'%s' is not one of this lab's condition names: %s."
                             % (c, ", ".join(sorted(CONDITIONS)))))
            continue
        seen.add(c)
        if st not in STATUS_VALUES:
            f.append(Finding("INCOMPLETE_REVIEW", "structure",
                             "observed['%s'].status must be 'same' or 'differs'." % c))
            continue
        gt = ground_truth(scenario, c)
        if gt == "not_exposed":
            # P2: reasoning claims to know something the artifacts do not expose.
            f.append(Finding("UNSUPPORTED_CITATION", "P2",
                             "Your review states that %s is '%s', but %s is not exposed by the "
                             "artifacts supplied for this scenario (%s). Nothing here establishes it."
                             % (c, st, c, ", ".join(sorted(scenario["a"].keys())))))
        elif st != gt:
            f.append(Finding("FACTUAL_CONTRADICTION", "P1",
                             "Your review states that %s is '%s', but the supplied artifacts show "
                             "'%s'." % (c, st, gt)))
        # P2 on cited evidence
        for ref in e.get("evidence", []) or []:
            side, _, art = str(ref).partition(".")
            if side not in ("a", "b") or art not in ARTIFACT_TYPES:
                f.append(Finding("UNSUPPORTED_CITATION", "P2",
                                 "Evidence reference '%s' is not of the form "
                                 "<a|b>.<result_record|job_summary|job_definition>." % ref))
            elif art not in scenario[side]:
                f.append(Finding("UNSUPPORTED_CITATION", "P2",
                                 "Your review cites %s as evidence for %s, but that artifact is not "
                                 "supplied in this scenario." % (ref, c)))
            elif art not in exposing_types(scenario[side], c):
                f.append(Finding("UNSUPPORTED_CITATION", "P2",
                                 "Your review cites %s as evidence for %s, but %s does not expose %s."
                                 % (ref, c, art, c)))

    # --- P2 over 'unknown'
    for e in review.get("unknown", []):
        c = e.get("condition")
        if c not in CONDITIONS:
            f.append(Finding("UNKNOWN_CONDITION", "structure",
                             "'%s' is not one of this lab's condition names." % c))
            continue
        seen.add(c)
        if ground_truth(scenario, c) != "not_exposed":
            where = exposing_types(scenario["a"], c)
            f.append(Finding("UNSUPPORTED_CITATION", "P2",
                             "Your review records %s as not determinable, but it is exposed by the "
                             "artifacts supplied here (%s)." % (c, ", ".join(where))))

    # --- P2 / structure over 'judgment'
    judged = {}
    for e in review.get("judgment", []):
        c, m = e.get("condition"), e.get("materiality")
        if c not in CONDITIONS:
            f.append(Finding("UNKNOWN_CONDITION", "structure",
                             "'%s' is not one of this lab's condition names." % c))
            continue
        judged[c] = e
        if m not in MATERIALITY_VALUES:
            f.append(Finding("INCOMPLETE_REVIEW", "structure",
                             "judgment['%s'].materiality must be one of %s. Which one you choose is "
                             "yours; the checker only needs a stated position."
                             % (c, ", ".join(MATERIALITY_VALUES))))
        if not str(e.get("reasoning", "")).strip():
            f.append(Finding("INCOMPLETE_REVIEW", "structure",
                             "judgment['%s'] has no reasoning. The reasoning is the review." % c))
        if c not in seen:
            f.append(Finding("UNSUPPORTED_CITATION", "P2",
                             "Your judgement reasons about %s, but %s appears in neither your "
                             "observed nor your unknown section. Record what you know about it "
                             "before reasoning from it." % (c, c)))

    # --- P3 claim-scope consistency
    # (a) Did you read the claim? A condition is in scope when the claim's own
    #     wording names it. This is a reading of the sentence you were given, not
    #     a judgement about whether the condition matters.
    declared = set(review.get("claim_puts_in_scope") or [])
    for c in sorted(declared - set(scoped)):
        f.append(Finding("CLAIM_SCOPE_CONFLICT", "P3",
                         "Your review lists %s as put in scope by the comparison claim, but the "
                         "claim's wording does not name it." % c))
    for c in sorted(set(scoped) - declared):
        f.append(Finding("CLAIM_SCOPE_CONFLICT", "P3",
                         "The comparison claim names %s (\"%s\"), but your review does not list it "
                         "among the conditions the claim puts in scope."
                         % (c, scoped[c].get("quote", ""))))

    # (b) and (c)
    for c, s in scoped.items():
        if c not in CONDITIONS:
            continue
        if c not in judged:
            f.append(Finding("CLAIM_SCOPE_CONFLICT", "P3",
                             "The comparison claim names %s (\"%s\"), but your review reaches no "
                             "judgement about it. The claim put it in scope."
                             % (c, s.get("quote", ""))))
            continue
        if ground_truth(scenario, c) == "differs" and judged[c].get("materiality") == "immaterial":
            f.append(Finding("CLAIM_SCOPE_CONFLICT", "P3",
                             "Your review classes the %s difference as immaterial, but the "
                             "comparison claim itself names %s (\"%s\"). That is inconsistent with "
                             "the claim you stated you were evaluating -- not with any rule this "
                             "tool holds about %s."
                             % (c, c, s.get("quote", ""), c)))
    return f


LIMITS = """  This checker verified three things and three things only:
    P1  factual statements about sameness and difference, against the supplied artifacts
    P2  that every condition your reasoning cites is exposed by the artifacts you hold
    P3  that your judgement does not contradict or ignore a condition the claim itself names

  WHAT THIS CHECKER DID NOT CHECK
    It does not determine whether two measurements are comparable, and it does not
    decide which observed differences are material. Those are your judgements. No
    answer key for them exists in this repository. AWS documents no list of fields
    that must match for two evaluation results to be comparable, and this lab does
    not invent one.

    A PASS means this review artifact passed the mechanical checks above.
    A PASS does not mean your comparison judgement is correct."""


def run(names=None):
    if not os.path.isdir(SCENARIOS):
        print("No scenarios directory found next to this script.")
        return 2
    names = names or sorted(n for n in os.listdir(SCENARIOS)
                            if os.path.isdir(os.path.join(SCENARIOS, n)))
    total, unauthored = 0, 0
    print("=" * 74)
    print("REVIEW CHECK -- validates your review, not comparability")
    print("=" * 74)
    for name in names:
        path = os.path.join(REVIEWS, "%s_review.json" % name)
        print("\n%s" % name)
        if not os.path.exists(path):
            print("  no review found at reviews/%s_review.json" % name)
            total += 1
            continue
        try:
            with open(path) as fh:
                review = json.load(fh)
        except ValueError as exc:
            print("  review is not valid JSON: %s" % exc)
            total += 1
            continue
        if has_placeholder(review):
            print("  not yet authored -- the scaffold still contains <FILL IN ...> markers.")
            unauthored += 1
            continue
        findings = check(load_scenario(name), review)
        if not findings:
            print("  PASS -- the mechanical checks found nothing to contradict.")
        else:
            for x in findings:
                print(str(x))
            total += len(findings)
    print("\n" + "-" * 74)
    print(LIMITS)
    print("-" * 74)
    if unauthored:
        print("\n%d review(s) not yet authored." % unauthored)
    print("%d finding(s)." % total)
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:] or None))
