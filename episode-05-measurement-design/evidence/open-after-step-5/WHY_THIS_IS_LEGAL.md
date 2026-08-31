# Why this design is legal — and what that does not establish

```json
"taskType":            "Summarization",
"dataset":             { "name": "handover-summaries-v1" },
"metricNames":         ["Builtin.Faithfulness", "Builtin.Completeness"],
"evaluatorModelConfig": "USE_JUDGE_MODEL",
"_lab.datasetFile":     "prompts_no_reference.jsonl"
```

---

## The measurement intent it represents

> *"Does the handover note say things the thread does not say, and does it leave out what the next
> agent needs?"*

Two concerns, from the team channel. **"It's mentioned a refund that wasn't in the thread"** is
invention. **"It leaves out the thing the customer is actually waiting for"** is omission. They are
not the same failure, and one instrument that answers only one of them answers half the question.

- `Builtin.Faithfulness` — AWS documents it as identifying whether the response contains
  information **not found in the prompt**. Invention.
- `Builtin.Completeness` — AWS documents it as measuring how well the response answers everything
  in the prompt. Omission.

---

## Why each choice is legal

**`evaluatorModelConfig` is set.** This is the choice that makes the rest of it possible.
`Builtin.Faithfulness` and `Builtin.Completeness` are documented for model evaluation jobs that use
a model as judge. With `evaluatorModelConfig` set to `null`, the only documented metric names are
`Builtin.Accuracy`, `Builtin.Robustness` and `Builtin.Toxicity` — **and neither of the two concerns
above could have been expressed at all.**

Notice the order that actually happened. The metrics did not choose the evaluator. **The evaluator
decided which metrics existed.** It was a decision about the instrument, made before anything was
measured, and it is easy to make without noticing.

**No reference answers.** `prompts_no_reference.jsonl` is used, and that is fine here: R3 requires
`referenceResponse` for `Builtin.Accuracy` and `Builtin.Robustness`, and neither is selected.
`Builtin.Faithfulness` in particular needs no reference by construction — it compares the response
against the prompt, not against a known-good answer.

**`taskType` and the dataset name.** Neither is checked. See N1 and N2 in `RULES.md` — AWS's own
documentation is inconsistent about both, so this lab enforces neither.

---

## Other designs that are also legal

| Design | Legal because |
|---|---|
| `evaluatorModelConfig: null` · `["Builtin.Accuracy"]` · `prompts_with_reference.jsonl` | automatic metric name, and every record carries a reference |
| `evaluatorModelConfig: null` · `["Builtin.Toxicity"]` · either dataset | R3 does not apply to `Builtin.Toxicity` |
| `USE_JUDGE_MODEL` · `["Builtin.Correctness"]` · `prompts_with_reference.jsonl` | AWS documents that a reference is used when supplied, and that the metric also works without one |
| `USE_JUDGE_MODEL` · `["Builtin.Relevance", "Builtin.Coherence"]` · either dataset | both documented for judge jobs |

**These are different instruments.** They do not answer the same question, and none of them is the
right one. That is the finding.

---

## What its legality does not establish

The checker accepted this design. That means one thing and nothing else: **it satisfies every
constraint the documentation states.**

It does **not** establish that:

- these two metrics capture what the team actually complained about — five things were said in that
  channel and this instrument addresses two;
- ten threads are the right ten, or enough of them;
- `Builtin.Completeness` means what an agent at 6am means by *complete* — one of the complaints was
  that the note is too long to skim, and nothing here looks at length;
- an evaluator model reads these threads the way a support agent does.

**None of those is a gap in the tooling.** They are the part of measurement design that is not
mechanical, and no checker in this lab or anywhere else will hand them to you.

That is the difference between a legal instrument and a good one — and the whole reason the
instrument has an author.
