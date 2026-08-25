# Lab guide — the response contract

**Do the steps in order.** Steps 2 and 3 come before you run anything, and that is the whole
experiment rather than an instruction to be polite about.

**Do not open `evidence/open-after-step-7/` until step 7.**

---

## Step 0 — Set up

Environment setup lives in **[`SETUP.md`](SETUP.md)** — a quick start if you set up Python
projects routinely, a guided version if you would rather have each command explained.

**You are ready for step 1 when `python scripts/preflight.py` says your environment is ready.**

Preflight checks your Python, your dependency, your AWS identity, your Region and your model
access. It exists so that anything surprising later is about the lab rather than about your
machine — a distinction that matters more here than in most labs.

**Run every command in this guide from the `episode-03-response-contract` directory**, with your
virtual environment activated.

---

## Step 1 — Read the requests · ~5 min

**What you are doing.** Reading `scripts/lab_requests.py`. Three requests. **Do not run it yet.**

**Why.** You are about to commit to a prediction, and you cannot commit to something you have not
read.

**What you should observe.** Three ordinary requests. One asks for a single word. One asks for
400 words and leaves very little room. One asks for a single word and leaves a great deal of
room.

**Next.** Step 2, before anything else.

---

## Step 2 — Predict · ~10 min · **the experiment starts here**

**What you are doing.** Filling in `PREDICTIONS.md`. All of it.

**Why.** Everything this lab teaches comes from the gap between what you write here and what
happens at step 4. Skip this and there is no gap, and no lab.

**What it demonstrates.** An engineer who cannot predict a system's behaviour does not yet
understand it. This is uncomfortable on purpose.

**How to interpret it.** You may be unsure. Write the uncertainty down — that is data too. Nobody
is marking this but you.

**Next.** Step 3. **Still do not run anything.**

---

## Step 3 — Build your interface · ~20 min

**What you are doing.** Implementing `handle()` in `scripts/contract.py`. It sends one request and
returns a result the rest of your application can act on.

**Why.** This is the exam skill's actual verb — *create FM API interfaces*. The deliverable is
the interface, not the script that calls it.

**What it demonstrates.** Whatever your interface does not carry, nobody downstream can recover.
Every field you drop is a decision you have made on behalf of every future caller.

**What you should observe.** You are designing a contract. Give it a shape you would be willing
to hand to another team.

**How to interpret it.** There is no single correct shape. There is a correct *coverage* — your
result should let a caller answer the four questions in the file's docstring without knowing
anything about Bedrock.

**Next.** Step 4.

---

## Step 4 — Run it · ~5 min

```
python scripts/lab_requests.py
```

Run it from the `episode-03-response-contract` directory with your environment activated. It prints
one block per request and writes nothing to disk.

**What you are doing.** Putting all three requests through your interface.

**Why.** To compare reality against what you wrote in `PREDICTIONS.md`.

**What you should observe.** **Record exactly what happened for each of the three — including
anything you did not expect.** Write it down before you react to it.

**How to interpret it.** Go through them one at a time against your predictions. **Do not fix
anything yet.** If something behaved unexpectedly, that is the lab working.

**Next.** Step 5.

---

## Step 5 — Explain it · ~15 min · **this is the step that matters**

**What you are doing.** Writing down, in your own words, why the third request behaved
differently from the first two.

**Why.** A correction is only worth making once you can say what it corrects. If you skip
to fixing the code you will fix the symptom and keep the assumption.

**What you should observe.** Where exactly did your code stop? Which line? What did that line
take for granted?

**How to interpret it.** Ask what a *caller of your interface* would have received. Not what
appeared in your terminal — what your caller would have got, and what they could have done with
it.

**Next.** Step 6, once you have written your answer.

---

## Step 6 — Correct the contract · ~20 min

**What you are doing.** Changing `handle()` so that all three requests return a usable result.

**Why.** An interface that raises on an outcome its underlying API genuinely produces has not
handled that outcome — it has forwarded it to everyone who calls you.

**What it demonstrates.** **An interface must be able to represent every outcome the API it wraps
can actually return** — including outcomes that arrive with no response at all.

**What you should observe.** You may find your original return shape cannot express the third
outcome without changing shape. That is the lesson rather than an inconvenience — the gap was in
the contract's structure, not in a missing `if`.

**How to interpret it.** Three things are genuinely different and your contract is more useful if
it keeps them apart:

- the SDK refused to send the request, so **AWS never saw it**
- the request reached AWS and AWS refused to run it
- inference ran, and told you how it ended

**Only the third has a termination signal to read.**

**Next.** Step 7.

---

## Step 7 — Validate · ~10 min

**What you are doing.** Re-running, then opening `evidence/open-after-step-7/`.

**Why.** Completeness is the objective.

**What you should observe.** All three requests return a result. None raises.

**How to interpret it.** Compare **states**, not words. Generated text differs between runs — ours
differed between our own two validation runs, with everything that matters identical. Read
`evidence/open-after-step-7/WHAT_MATCHES.md` before you compare anything.

### You are done when

1. `PREDICTIONS.md` was filled in before step 4.
2. All three requests return a result and none raises.
3. Your contract distinguishes *never sent* from *rejected* from *answered*.
4. It carries the termination signal where there is one, and does not invent one where there is
   not.
5. Your step 5 explanation is in your own words.

**Next.** Step 8.

---

## Step 8 — Cleanup · ~2 min

Nothing was created, so nothing is torn down. See `CLEANUP.md` — it is short, and worth reading
rather than assuming.

---

## Where this goes next

You now have an interface that reports what happened rather than only what was said. Three of the
outcomes you handled will come back identically however many times you send the request again.
One of them will not. Which one, and what your interface should do about it, is a different
problem with a different answer.
