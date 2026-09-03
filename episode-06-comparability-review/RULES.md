# Rules

Read this before you start. It tells you what the checker can and cannot decide,
so that nothing it says — or doesn't say — misleads you.

---

## 1. What this lab asks

You are given, for each scenario:

- **a comparison claim**, written out in one sentence;
- **two measurements**, A and B, as local JSON artifacts;
- **only the information available at that scenario's altitude.** Different
  scenarios supply different artifacts. That is deliberate.

You write a review that answers, for that claim:

> **What changed between these two measurements, what do I actually know about
> that change from the artifacts in front of me, and does it matter to the
> comparison I am being asked about?**

Every configuration here is **legal**. Nothing is malformed. Legality was the
previous question.

---

## 2. Where the facts live

The same fact is not available everywhere. This lab supplies three kinds of
artifact, and each carries different things.

| | `result_record` | `job_summary` | `job_definition` |
|---|---|---|---|
| model | yes | yes | yes |
| task type | yes | yes | yes |
| dataset | yes | **no** | yes |
| metric name | yes | **no** | yes |
| evaluator model | **no** | ambiguous — see below | yes |
| inference parameters | **no** | **no** | yes |
| reference response present | yes | **no** | **no** |

**This is not a hierarchy and it is not a procedure.** It is not a sequence you
perform. Notice the last row: the lowest-detail artifact is the only one that
carries something. "More detailed" does not mean "contains everything the others
contain."

**On the evaluator model.** A returned job definition with no
`evaluatorModelConfig` establishes that no evaluator model was configured — that
is a fact. A job summary with an empty `evaluatorModelIdentifiers` list is
ambiguous between "none" and "none reported", so this lab does not read it as
establishing the condition either way.

Every field above traces to current AWS documentation. See `SOURCE_MAP.json`.

---

## 3. What `check_review.py` can decide

It is a **review checker**. It validates limited properties of what you wrote.
**It does not determine comparability.**

Three things. This list is closed.

**P1 — Factual verification.**
Does a statement you made about sameness or difference agree with the artifacts
this scenario supplied?

**P2 — Evidence-provenance verification.**
Does the artifact you are holding actually expose the condition your reasoning
claims to know about? If you state that the inference parameters are identical
while holding only a result record and a job summary, neither of which carries
them, the checker will say so.

**P3 — Claim-scope consistency.**
Three things, all read off the claim sentence you were given.

First, *did you read it?* Your `claim_puts_in_scope` must list exactly the
conditions the claim's own wording names — no more, no fewer. **A condition is in
scope when the claim names it.** Each scoped condition quotes the phrase in the
claim that names it, so you can check your reading against the sentence. This is
a reading of the claim, not a judgement about whether the condition matters.

Then: does your reasoning contradict or ignore that scope? If the claim says the values
are being read *over a named dataset*, and the two jobs used different datasets,
you cannot record that difference as immaterial — not because of any rule this
tool holds about datasets, but because **the claim you said you were evaluating
named it.**

---

## 4. What it cannot decide, and will not pretend to

**It does not decide whether two measurements are comparable, and it does not
decide which observed differences are material.**

There is no answer key for those questions anywhere in this repository. Not in
the tests, not in the scenario files, not in a comment, not in a filename. **AWS
documents no list of fields that must match for two evaluation results to be
comparable, and this lab does not invent one.**

The checker will never emit:

- COMPARABLE or NOT COMPARABLE
- a comparability score or a materiality score
- a correct, expected or recommended materiality label
- a winning model, a ranking or a recommendation
- a list of fields that must match

**And it will not smuggle any of those in as a warning, a hint or a severity
label.** A warning that a difference "might matter" would be a materiality
judgement wearing a disclaimer. If the checker is silent about a difference,
that silence means *it has no view*, not *it approves*.

---

## 5. Materiality is not field equality

**Matching more fields is not better. Differing is not failing.**

A difference between two measurements is one of three things:

- **material** — the claim cannot survive it;
- **immaterial** — the claim is untouched by it;
- **cannot classify** — you do not have what you would need to say.

**Which one it is depends on the claim being made, not on the field.** The same
difference can be fatal to one comparison and irrelevant to another. Two
measurements produced under identical conditions are not automatically
comparable, and two produced under differing conditions are not automatically
incomparable.

**"I cannot determine this from the artifacts I currently hold" is a legitimate
engineering finding.** It is a correct answer, not a failure to find one, and
nothing in this lab penalises it. Recording an unknown honestly is stronger than
asserting something you cannot see.

---

## 6. What PASS means

**PASS means: this review artifact passed the checker's limited mechanical
checks.** Its factual statements agree with the artifacts, the conditions it
cites are ones the artifacts expose, and its reasoning does not contradict the
claim's own declared scope.

**PASS does not mean your comparison judgement is correct.** The checker has no
opinion on your judgement. Two reviews reaching opposite conclusions about the
same difference can both pass, and that is intended.

**There is no score. There are no points. There is no pass quality rating.**

---

## 7. What this lab stops short of

You may conclude:

> *"I would / would not directly compare these measurements without addressing X."*

You may **not** conclude which model to use. There is no field in the review
artifact for a winner, a ranking, a preferred model, a deployment recommendation
or a cost comparison — deliberately. **Deciding what to do about a comparison is
a different act from establishing that the comparison holds**, and this lab is
only about the second one.

---

## Notes — what this lab deliberately does not decide

**N1.** AWS publishes no field-level comparability rule. The condition list in
§2 is a list of **things you can look at**, assembled from what the documented
artifacts expose. **It is not a list of things that must match**, and it is not
exhaustive of everything that could bear on a comparison.

**N2.** The `claim_scoped_conditions` in each `scenarios/scenario_NN/claim.json` are a **reading of the
claim sentence** — each one quotes the phrase in the claim that names it. They
record what the claim put in scope. **They are not materiality labels and they
carry no expected answer.** A condition being in scope says nothing about whether
a difference in it is material; that is still entirely yours to argue. What scope
does settle is narrow: you cannot call a difference immaterial in a condition
your own claim named.

**N3.** P2 asks a narrow question: *is the condition your reasoning cites exposed
by the artifacts you hold?* It is a question about **provenance**, not about
adequacy. It never asks whether your evidence is enough for some purpose. That
is a different question and this lab does not ask it.

**N4.** Every value in `scenarios/` is invented for this exercise. The shapes
follow current AWS documentation; **the numbers, names and responses are not
observed AWS output** and must not be cited as such. See `SOURCE_MAP.json`.

**N5.** This lab makes no claim about the quality, behaviour or suitability of
any model it names. Model identifiers appear as realistic values, nothing more.
