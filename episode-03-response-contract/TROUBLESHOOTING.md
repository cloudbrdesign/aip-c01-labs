# Troubleshooting

**Two different kinds of problem, kept apart on purpose.**

| | |
|---|---|
| **[Setup and environment problems](#setup-and-environment-problems)** | Something is wrong with your machine, your credentials or your access. **Fix these.** |
| **[While running the lab](#while-running-the-lab)** | The lab ran. Something happened you did not expect. **These are not defects, and this page will not resolve them for you.** |

If you have not run `python scripts/preflight.py` yet, run it first. It exists to keep the first
category out of the second.

---

## Setup and environment problems

### `python3: command not found` / `python: command not found`

Python is not installed, or not on your PATH. Install it from python.org — on Windows, tick **"Add
Python to PATH"**. If `python` is missing but `py` works, use `py -3` wherever the instructions say
`python`.

### `ModuleNotFoundError: No module named 'boto3'`

Almost always an environment that is not activated. Check your prompt for `(.venv)`.

```bash
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Your system Python may not have boto3 even if the AWS CLI works — the CLI bundles its own copy and
does not share it.

### PowerShell refuses to activate the environment

An execution-policy restriction. Either allow it for that window only:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

or use `.venv\Scripts\activate.bat` from `cmd.exe` instead.

### `NoCredentialsError`, or preflight reports credentials could not be resolved

boto3 found no credentials. Configure them (`aws configure` is the simplest route), or point your
terminal at an existing profile with `AWS_PROFILE`. See `SETUP.md` step 6.

### Preflight says the credentials are root

Use an IAM user or role instead. Preflight refuses root deliberately — running labs as root is a
habit worth not forming.

### `AccessDeniedException` on the model-access check

Two distinct causes, and they need different fixes.

- **Model access is not enabled.** Enable it for your chosen model in the Bedrock console, **in the
  Region you are calling**. Access is granted per account and per Region.
- **Your IAM policy does not cover the id you are using.** A plain model id and a cross-Region
  inference profile id are different resources. Scope `bedrock:InvokeModel` to the id you actually
  set in `LAB_MODEL_ID`.

### The model id is not recognised, or is unavailable in your Region

Not every model is available in every Region, and some are reachable only through a cross-Region
inference profile rather than their plain id. Check the model's page in the AWS documentation for
which forms exist where, then set `LAB_MODEL_ID` accordingly.

### Wrong Region

`AWS_REGION` controls it. If it is unset, the lab uses `us-east-1`. Model availability and model
access are both per-Region, so a Region mismatch usually shows up as an access or unknown-model
error rather than as a Region error.

### Preflight passes but I want to use a different model

Set `LAB_MODEL_ID` and run preflight again. The lab does not depend on any particular model.

---

## While running the lab

### Something behaved in a way I did not predict

**That is data, not a defect.**

Record exactly what you saw and continue to **step 5** of `LAB_GUIDE.md`. Do not change your
implementation yet, and do not go looking for the answer — working it out is the lab.

**This page deliberately does not tell you what to expect from any individual request.** If it did,
there would be nothing left to find out.

### I am stuck at step 6 and cannot see what to change

Re-read what you wrote at **step 5**. If you have not written it yet, write it — most people who are
stuck at step 6 skipped step 5, and the answer tends to fall out of stating the problem properly.

If you are still stuck after a genuine attempt, `evidence/open-after-step-7/` contains a reference
implementation. Using it after you have tried is fine. Reading it before step 5 removes the point of
the exercise.

### My results do not match the captured evidence exactly

Expected. Generated text differs between runs — ours differed between our own two validation runs.
`evidence/open-after-step-7/WHAT_MATCHES.md` sets out precisely what should match and what should
not. Compare the states, not the words.
