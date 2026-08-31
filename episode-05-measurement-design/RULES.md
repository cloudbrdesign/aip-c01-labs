# What the checker enforces, and what it refuses to

`rules_sources.json` is the machine-readable version of this file. The checker reads it; so can
anything else that needs to know which AWS relationships this lab depends on.

Every rule below is enforced **only** because Amazon Bedrock's documentation states it. Nothing
here is inferred, and nothing was added to make the exercise harder.

---

## Enforced

### Primary — these two are what the lab is about

| Rule | Condition | Source |
|---|---|---|
| **R1** | When `evaluatorModelConfig` is **absent**, every `metricNames` entry must be one of the names AWS documents as valid for automated model evaluation jobs: `Builtin.Accuracy`, `Builtin.Robustness`, `Builtin.Toxicity`. | `S-DATASETMETRIC` |
| **R3** | When a **custom** prompt dataset is used with `Builtin.Accuracy` or `Builtin.Robustness`, every record must carry `referenceResponse`. | `S-PROMPTDATASETS` |

### Also enforced

| Rule | Condition | Source |
|---|---|---|
| **R2** | When `evaluatorModelConfig` is **present**, every `metricNames` entry must be a name AWS documents as valid for *some* model evaluation configuration — the judge set or the automated set. A name in neither is not a valid value under any reading. **Corrected 2026-08-31 — see N5.** | `S-DATASETMETRIC` |
| **R4** | `datasetMetricConfigs` holds between 1 and 5 items. | `S-AUTOEVALCONFIG` |
| **R5** | `metricNames` holds between 1 and 25 items. | `S-DATASETMETRIC` |
| **R6** | A custom prompt dataset holds at most 1000 prompts. | `S-PROMPTDATASETS` |
| **R7** | When you supply your own inference responses, exactly one unique `modelIdentifier` appears, on every record. | `S-JUDGEDATASETS` |

**R4–R7 are hygiene.** If one of them is the only thing standing between you and a valid design,
you have a counting problem, not a design problem.

---

## Deliberately NOT enforced

A validator should enforce what its evidence supports, and no more. These are left alone on
purpose, and the checker says so every time it runs.

### N1 — `taskType` values are not checked

AWS's API reference lists the valid values as `Summarization`, `Classification`,
`QuestionAndAnswer`, `Generation` and `Custom`. AWS's own model-as-a-judge examples use
`"taskType": "General"`, which is not in that list.

**The evidence contradicts itself.** Enforcing either version would fail somebody for following
AWS's own example, so no `taskType` value is accepted or rejected here.

### N2 — built-in dataset name casing is not checked

The same dataset appears in AWS's documentation as both `Builtin.BOLD` and `Builtin.Bold`.

### N3 — the task-to-dataset relationship is not enforced

AWS documents which datasets are *recommended* for a task type, and which ones the console
*offers* once you pick one. **Recommended is not required.** Enforcing it would invent a
constraint.

### N5 — whether an evaluator model makes the automated metric names invalid is not checked

AWS documents one set of metric names for automated model evaluation jobs — `Builtin.Accuracy`,
`Builtin.Robustness`, `Builtin.Toxicity` — and another for jobs that use a model as judge. It says
three responsible-AI metrics are available *"only for"* judge jobs, which is an explicit,
**one-directional** restriction, and R1 enforces that direction.

**It does not say the reverse.** Nothing states that the automated names stop being valid once an
evaluator is configured. The API also nests judge jobs *inside* `automated`, which leaves the phrase
"automated model evaluation jobs" genuinely ambiguous about whether it includes them.

**Listing different sets for different configurations is not the same as declaring them mutually
exclusive**, so this checker no longer treats it as one.

**It does not warn about it either.** A warning would still imply the checker knows your
configuration is questionable, and it does not know that.

> **Corrected 2026-08-31, after publication.** An earlier version of R2 rejected
> `Builtin.Accuracy`, `Builtin.Robustness` and `Builtin.Toxicity` whenever an evaluator model was
> configured. That was an inference presented as a documented constraint. It has been removed. R1
> and R3 are unchanged, and the exercise is unchanged.

### N4 — whether your design measures what you meant is not checked, and cannot be

This is the important one.

The checker can tell you that a configuration is legal. It cannot tell you that it is a good
measurement of the thing you wrote down in step 1. Those are different questions, and only one of
them is mechanical.

**A design can satisfy every rule on this page and still measure something other than what you set
out to learn.** No tool in this lab will catch that. You will.

---

## Sources

| ID | Document |
|---|---|
| `S-DATASETMETRIC` | Amazon Bedrock API Reference — `EvaluationDatasetMetricConfig` |
| `S-AUTOEVALCONFIG` | Amazon Bedrock API Reference — `AutomatedEvaluationConfig` |
| `S-PROMPTDATASETS` | Amazon Bedrock User Guide — *Use prompt datasets for model evaluation* |
| `S-JUDGEDATASETS` | Amazon Bedrock User Guide — *Create a prompt dataset for a model evaluation job that uses a model as judge* |

URLs are in `rules_sources.json`, and the checker prints the relevant one with every finding.

**Retrieved 2026-08-31.** AWS documentation changes. If a rule here stops matching the live
documentation, the rule is wrong, not the documentation — please open an issue.
