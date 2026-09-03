# Comparability review

**A local exercise. No AWS account. No credentials. No network. No cost.**

You have two finished measurements and one number is higher than the other.
Before you can read them side by side, something has to be true about how they
were produced. This lab is about working out whether it is.

---

## Requirements

- **Python 3.9 or newer. Standard library only.** Nothing to install.
- No AWS account, no credentials, no network access, no cost, and nothing to
  clean up afterwards. Nothing here calls AWS.

```
python3 --version
```

---

## What you do

**Read `RULES.md` first.** It tells you what `check_review.py` can and cannot
decide. That matters more here than in most exercises, because it deliberately
refuses to answer the interesting question.

Then, for each scenario:

1. **Read the claim.** `scenarios/scenario_NN/claim.json` states, in one
   sentence, the comparison you are being asked about. **Everything else in the
   scenario is read against that sentence.** A difference is not material in
   general — it is material *to a claim*.

2. **Read the artifacts.** Each scenario supplies measurement A and measurement
   B as local JSON. **Different scenarios supply different artifacts.** Check
   what you actually have before you reason from it.

3. **Author your review** in `reviews/scenario_NN_review.json`. Replace every
   `<FILL IN ...>` marker. One field, `claim_puts_in_scope`, asks which conditions
   the claim's own wording names — that is a reading of the sentence, not a
   judgement about whether they matter.

4. **Then** run `check_review.py`.

```
python3 check_review.py                # all scenarios
python3 check_review.py scenario_01    # one scenario
```

While a review still contains `<FILL IN ...>` markers, `check_review.py` reports
it as not yet authored and checks nothing. **Author first, run second.** The
commitment is the point.

---

## Your review has three kinds of content, and only two are checkable

| Section | What it is | Checked? |
|---|---|---|
| `claim_puts_in_scope` | Which conditions the **claim's own wording names** | **Yes** — against the claim sentence |
| `observed` | What the supplied artifacts **do** establish | **Yes** — against the artifacts |
| `unknown` | What the supplied artifacts **do not** establish | **Yes** — against the artifacts |
| `judgment`, `would_compare`, `before_comparing` | What **you** conclude | **No.** Read for completeness and, where the claim itself settles the point, for internal consistency |

That split is the lesson, not an implementation detail. **`check_review.py` verifies
facts about your review. You own the judgement.**

---

## Three things worth knowing before you start

**Every configuration here is legal.** Nothing is malformed, nothing is invalid,
nothing will fail to run. Whether a measurement design is valid was the previous
question. This one starts after that.

**"I cannot determine this from the artifacts I currently hold" is a legitimate
finding.** Some conditions are not exposed by some artifacts. When that happens,
say so — record it in `unknown`. It is a correct answer, not a failure to find
one, and nothing here penalises it. Asserting something you cannot see is the
error this lab is looking for; admitting a gap is not.

**Matching more fields is not better.** Two measurements produced under identical
conditions are not automatically comparable, and two produced under differing
conditions are not automatically incomparable. There is no checklist, here or at
AWS. See `RULES.md` §5 and N1.

---

## Files

```
README.md                  this file
RULES.md                   what check_review.py can and cannot decide -- read it first
SOURCE_MAP.json            every AWS-derived shape, traced; and what is invented
scenarios/                 the claims and the measurement artifacts
reviews/                   your work goes here
check_review.py            the review checker -- it validates your review, not comparability
tests/                     tests for check_review.py itself
```

**Everything in `scenarios/` is synthetic and course-authored.** The shapes
follow current AWS documentation; the numbers, names and responses are invented
for this exercise and are **not** observed AWS output. `SOURCE_MAP.json` records
which is which, field by field.

---

## Running the tests

You do not need to. They test `check_review.py`, not your review.

```
python3 -m unittest discover -s tests -v
```

---

## What this exercise is not

It does not tell you which model to use. There is no field in the review
artifact for a winner, a ranking, a recommendation or a cost comparison, and
that is deliberate. **Deciding what to do about a comparison is a different act
from establishing that the comparison holds.** This is only the second one.
