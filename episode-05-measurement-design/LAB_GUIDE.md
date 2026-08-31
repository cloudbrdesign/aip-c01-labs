# Lab guide — building a measurement instrument

**Time:** 25–35 minutes, most of it thinking · **Cost:** $0 · **AWS account:** not required

Read `SCENARIO.md` first and write your sentence. This guide assumes you have.

---

## What you are actually building

Amazon Bedrock's `CreateEvaluationJob` request has two separately-required parts:

```
CreateEvaluationJob
├── inferenceConfig    ← the thing being measured
└── evaluationConfig   ← the measurement
```

They are siblings. **The measurement is not a property of the model — it is a separate artifact
that you supply alongside it.** This lab is about the second one.

Inside `evaluationConfig.automated`, three choices are bound together in one required object:

```
datasetMetricConfigs
├── taskType
├── dataset
└── metricNames
```

and one optional field sits beside it:

```
evaluatorModelConfig      ← optional. AWS: "This model computes all evaluation related metrics."
```

`my_design.json` mirrors that shape. Its `_lab` block does not — that exists only so this can run
with no AWS account.

---

## Step 1 — State what you want to know

**WHAT YOU ARE DOING:** writing one sentence, in plain words, before any configuration exists.

**WHY:** because in a moment you will start choosing from lists, and lists are persuasive. The
sentence is the only record of what you wanted before the options shaped it.

**WHAT TO OBSERVE:** whether your sentence is one concern or several wearing one coat. "Is it any
good" is usually four questions.

Write it in `EVIDENCE_TEMPLATE.md` under **A**.

---

## Step 2 — Commit to a design

**WHAT YOU ARE DOING:** filling in the five values marked `<CHOICE n: ...>` in `my_design.json`.

| | Choice | Where |
|---|---|---|
| 1 | `taskType` — what kind of task is the model performing? | `datasetMetricConfigs[0].taskType` |
| 2 | `dataset.name` — a name for your own dataset, or a `Builtin.*` dataset | `datasetMetricConfigs[0].dataset.name` |
| 3 | `metricNames` — one or more metric names | `datasetMetricConfigs[0].metricNames` |
| 4 | `evaluatorModelConfig` — `null`, or `USE_JUDGE_MODEL` | `automated.evaluatorModelConfig` |
| 5 | which prompt dataset file to use | `_lab.datasetFile` |

**Edit values only.** Braces, brackets, commas and quotes are already correct and are not part of
this exercise. If you break the structure the checker will tell you, and it will call it a tooling
problem, because it is one.

**On choice 4.** `USE_JUDGE_MODEL` is a stand-in this lab understands. In a real request that field
holds:

```json
"evaluatorModelConfig": {
  "bedrockEvaluatorModels": [
    { "modelIdentifier": "<a supported evaluator model id>" }
  ]
}
```

Set it to `null` if you do not want one. Both are real choices.

**On choice 5.** Two prompt datasets ship with the lab, built from the same ten threads:

- `prompts_with_reference.jsonl` — each record carries a `referenceResponse`: a handover note
  written by a person, for that thread.
- `prompts_no_reference.jsonl` — the same prompts, with no reference answers.

Choosing between them is a design decision, not a convenience. Open both.

**WHAT PRINCIPLE THIS DEMONSTRATES:** every one of these five is a decision, and four of them are
easy to make without noticing you made one.

Record your choices in `EVIDENCE_TEMPLATE.md` under **B**.

---

## Step 3 — Predict, before you run anything

**WHAT YOU ARE DOING:** writing down two things.

1. Do you expect this configuration to be valid?
2. **For each metric you selected — what is it intended to tell you about your step 1 sentence?**

The second is the one that matters. One line per metric.

**WHY:** if you run the checker first, you will never know what you believed.

Record under **C**. Do not skip this step; it is the lab.

---

## Step 4 — Run the checker

```bash
python3 scripts/check_design.py
```

It reads your design and your chosen dataset, and reports whether the configuration satisfies
constraints AWS documents. It does not run an evaluation, produce a result value, or contact AWS.

Record what it said under **D**.

---

## Step 5 — Read any finding, and its source

**WHAT TO OBSERVE:** each finding names a rule ID, states the condition that was not satisfied,
and links the AWS page it comes from.

**HOW TO INTERPRET IT:** the checker will not tell you what to change. That is deliberate. Read the
condition and work out which of your five choices put you outside it — and notice that it may not
be the choice the message names.

**If your first design was valid, go to §8 now.** You have not missed anything.

---

## Step 6 — Revise your design, not the file structure

Change one of the five values. Run the checker again.

**WHAT TO OBSERVE:** whether the choice you changed is the one you would have predicted needed
changing.

---

## Step 7 — Reach a valid configuration

Repeat until the checker reports valid. Record the final configuration under **E**.

**More than one configuration is valid.** There is no answer key here, and the checker is not
comparing you to a preferred design. It is asking one question: is this legal under the documented
constraints?

---

## Step 8 — Compare the instrument with the intent

**This is the point of the lab.** Put your step 1 sentence next to your final configuration and
answer, in `EVIDENCE_TEMPLATE.md` under **F**:

1. Does the configuration measure what the sentence asked for?
2. If not — what changed, and *when* did it change? Was it when you picked the metrics, or earlier?
3. Which of your five choices constrained the others?
4. **What has the checker not established about your design?** (`RULES.md`, N1–N4.)

### If your first design passed

Answer these four instead, in the same place. A design that was legal first time is not a smaller
result — but it is only evidence of understanding if you can say why.

1. What was your step 1 measurement intent?
2. What is each selected metric intended to contribute to it?
3. Which evaluator and reference-data choices make those metrics legal — and what would have
   happened to your metric list if you had chosen the other way?
4. What has the checker **not** proved about the quality of your design?

---

## Then, and only then

`evidence/open-after-step-5/` holds **one** valid design and an explanation of why it is legal.
It is one design. It is not the design. Read it after you have your own.

---

## Cleanup

None. Nothing was created outside this directory, and no cloud resource exists. Delete the folder
if you want the space back.
