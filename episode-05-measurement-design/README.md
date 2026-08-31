# Episode 5 — Build a measurement instrument

Companion lab for **Episode 5** of *What AIP-C01 Actually Tests*.
Blueprint skill **5.1.1** — *Develop comprehensive assessment frameworks to evaluate the quality
and effectiveness of FM outputs beyond traditional ML evaluation approaches.*

---

|  |  |
|---|---|
| **Runs on** | your laptop |
| **AWS account** | **not required** |
| **AWS credentials** | **not required, and never looked for** |
| **Network access** | not required |
| **Cloud resources created** | **none** |
| **Cost** | **$0** |
| **Cleanup** | **none** — delete this directory if you want the space back. No cloud resources were created. |
| **Dependencies** | Python 3.9+, standard library only. No packages to install. |
| **Time** | 25–35 minutes |

---

## What this lab is

You are given a real measurement problem and a valid configuration scaffold. You decide **what to
measure, on what, and by what rule** — then a local checker tells you whether the configuration you
built satisfies constraints that Amazon Bedrock's documentation states.

The interesting part is not whether you pass. It is what you find out about the design you
committed to before you ran anything.

## What this lab is not

It does not run an evaluation. It does not contact AWS. It produces **no result values of any
kind** — nothing is measured, nothing is rated, nothing is compared. It has no opinion about which
measurement you should have picked, and it will not tell you.

It also cannot tell you whether your design measures what you meant. See **N4** in `RULES.md` —
that limit is deliberate, and it is most of the lesson.

---

## Setup

```bash
git clone https://github.com/cloudbrdesign/aip-c01-labs.git
cd aip-c01-labs/episode-05-measurement-design

python3 --version          # 3.9 or newer

python3 scripts/preflight.py
```

There is no `requirements.txt`, because there is nothing to install. If you prefer to work in a
virtual environment you can, but this lab does not need one:

```bash
python3 -m venv .venv && source .venv/bin/activate      # optional
```

`preflight.py` checks your Python version and that the lab's files are present and readable. It
does not look for AWS credentials, read AWS configuration, or open a network connection.

---

## Do the lab

1. Read **`SCENARIO.md`** and write your one sentence. Do this first.
2. Follow **`LAB_GUIDE.md`**, steps 1–8.
3. Record what you did in **`EVIDENCE_TEMPLATE.md`**.

```bash
python3 scripts/check_design.py
```

---

## Files

| | |
|---|---|
| `SCENARIO.md` | the problem, and the sentence you write before anything else |
| `LAB_GUIDE.md` | the eight steps |
| `EVIDENCE_TEMPLATE.md` | what to record |
| `RULES.md` | every rule the checker enforces, its source, and the four it refuses to enforce |
| `my_design.json` | **the file you edit** — valid already; change only the five marked values |
| `prompts_with_reference.jsonl` | ten prompts, each with a human-written reference answer |
| `prompts_no_reference.jsonl` | the same ten prompts, without reference answers |
| `rules_sources.json` | machine-readable rule → AWS source register |
| `scripts/preflight.py` | local environment check |
| `scripts/check_design.py` | the constraint checker |
| `tests/test_checker.py` | the checker's own tests |
| `evidence/` | **contains a worked design — do not open before step 5** |
| `TROUBLESHOOTING.md` | when something does not run |

There is no `infra/`, no `ARCHITECTURE.md` and no `CLEANUP.md`, because this lab provisions
nothing. Empty files that exist only to resemble a cloud lab would be worse than their absence.

---

## Running the tests

You do not need to. If you want to see what the lab guarantees about itself:

```bash
python3 tests/test_checker.py
```

They check that each rule fires when it should, that the four unenforced ones stay unenforced, that
the checker never recommends a design, that more than one design passes, and that nothing from
later in the course leaks into this one.

---

## Licence

Apache-2.0. See the repository root.

Independent educational project. Not affiliated with, endorsed by, or sponsored by Amazon Web
Services. AWS documentation is cited and linked, not reproduced.
