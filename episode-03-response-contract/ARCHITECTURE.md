# Architecture

## Resources created

**None.** No endpoint, model deployment, store, index, cache, bucket, log group, IAM principal or
repository is created by this lab. There is nothing to tag and nothing to tear down.

## Shape

```
your machine                          AWS
─────────────                         ───
scripts/contract.py   ──request──▶    bedrock-runtime:Converse
  (you write this)    ◀──result───
```

That is the whole system. The lab is small on purpose: everything interesting is in what your
interface does with what comes back.

## Services and permissions

| | |
|---|---|
| **Service** | `bedrock-runtime` — the `Converse` operation only |
| **Permission** | `bedrock:InvokeModel`, scoped to the model you choose |
| **Not needed** | Anything else. No `CountTokens`, no S3, no CloudWatch, no IAM changes |

## Model selection

`scripts/lab_requests.py` defaults to one Converse-capable model and reads `LAB_MODEL_ID` if you
set it. **The lab does not depend on which model you use** and contains no model's numbers.

One request deliberately asks for far more output capacity than any current model provides. It
does that with a single obviously-excessive value rather than a specific ceiling, because output
ceilings differ by model and change over time. If the service has something to say about that
value, what it says will be about the model *you* chose, on the day you ran it — treat it as a
fact about that model, not a fact about Bedrock.

## Cost

| | |
|---|---|
| Requests that generate output | Two. One of them is capped at 24 output tokens by construction |
| Requests that generate nothing | One |
| Resources billed after the session | **None. Nothing persists** |

No price is quoted here. Bedrock rates are per-model and per-Region and change; if you want a
number, take it from the current pricing page for the model and Region you actually used.

## Deliberately not included: the context-window state

The episode describes a response state that arises when a conversation grows past the model's
context window. **This repository contains no evidence of that state and does not ask you to
produce it.**

That is a deliberate gap, and it is honest about itself: producing that state means sending an
input close to the size of the model's context window, repeatedly, which is the one part of this
subject that is not cheap. A captured example may be added later. **Until it is, nothing in this
repository should be read as demonstrating it**, and you should not infer its behaviour from the
requests that are here — they are different conditions.
