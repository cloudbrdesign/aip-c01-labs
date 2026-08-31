# Troubleshooting

## `python3: command not found`

Try `python --version`. If it reports 3.9 or newer, use `python` in place of `python3` throughout.
On Windows, `py -3` also works.

## Preflight says a file is missing

You are probably not in the lab directory. From the repository root:

```bash
cd episode-05-measurement-design
python3 scripts/preflight.py
```

## The checker says `TOOLING: ... is not valid JSON`

You changed the structure rather than a value. **This is not part of the exercise** — the file
shipped valid.

The message gives a line and column. Common causes: a deleted comma between two entries, a missing
closing quote, or a `"` typed as a curly quote by an editor with smart quotes on.

If you want to start over, restore the file:

```bash
git checkout my_design.json
```

Your evidence notes are in a different file and are not affected.

## The checker says the design still holds scaffold placeholders

One of the five `<CHOICE n: ...>` values has not been replaced yet. The message names which.

Replace the **whole** placeholder string including the angle brackets. For example
`"taskType": "<CHOICE 1: ...>"` becomes `"taskType": "Summarization"` — quotes kept, brackets gone.

## `evaluatorModelConfig` — what do I actually put there?

Either `null` (no quotes — it is a JSON null) or the string `"USE_JUDGE_MODEL"` (with quotes).
`LAB_GUIDE.md` step 2 shows what the real AWS field looks like.

## The checker reported a rule I do not understand

Every finding names a rule ID. `RULES.md` states the condition in full and links the AWS page it
comes from. The link in the finding goes to the same place.

## My first design passed and I feel like I missed something

You did not. `LAB_GUIDE.md` step 8 has a set of questions for exactly this case. Answer those.

## The checker will not tell me what to change

Correct. It reports which documented condition your configuration does not satisfy, and where that
condition is written down. Working out which of your five choices caused it is the exercise.

## Does any of this cost money or touch my AWS account?

No. Nothing here opens a network connection, reads AWS configuration, or looks for credentials.
`python3 tests/test_checker.py` asserts that, if you would rather check than trust.
