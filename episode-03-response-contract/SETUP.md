# Setup

Two paths to the same place. **Both end with a passing preflight and you at step 1 of
`LAB_GUIDE.md`.** Pick whichever suits you; there is no difference in the lab itself.

- **[Path A — Quick start](#path-a--quick-start)** if you set up Python projects routinely.
- **[Path B — Guided setup](#path-b--guided-setup)** if you would rather be told what each command
  does and what to do when one fails.

**This page helps you run the lab. It does not tell you anything about what the lab shows you.**

---

## Prerequisites

Checked against what the lab actually does, not against a generic list.

### Required

| | Why |
|---|---|
| **Python 3.9 or newer** | The lab is a small Python program. Preflight checks your version |
| **`pip`** | Ships with Python. Installs the one dependency |
| **`boto3`** | The AWS SDK for Python. **Installed by you into a virtual environment** — see below. Do not install it globally |
| **An AWS account you control** | The lab calls a real AWS service |
| **AWS credentials configured locally** | So the SDK can authenticate as you |
| **`bedrock:InvokeModel`** on the model you use | **The only IAM permission this lab requires.** See [IAM](#iam--the-minimum) |
| **Access enabled for one text model** | Model access is granted per account and per Region. Preflight checks it |

### Optional

| | Why it is only optional |
|---|---|
| **Git** | Convenient for getting the files. Downloading the repository as a ZIP works identically |
| **AWS CLI** | Handy for configuring credentials and for your own checks. **The lab never calls it** — preflight verifies your identity through boto3 |
| **A named AWS profile** | One of several valid ways to supply credentials. Any mechanism boto3 understands is fine |

### Not required

**Docker · Terraform · CloudFormation · an IDE · a specific operating system · `AdministratorAccess`
· a dedicated AWS account · any AWS service other than Bedrock Runtime.**

The lab **creates no AWS resources at all**, so there is nothing to provision and nothing to clean
up on the AWS side.

---

## Path A — Quick start

```bash
git clone https://github.com/cloudbrdesign/aip-c01-labs.git
cd aip-c01-labs/episode-03-response-contract

python3 --version                      # need 3.9+
python3 -m venv .venv
source .venv/bin/activate              # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

export AWS_REGION=us-east-1            # Windows PowerShell: $env:AWS_REGION="us-east-1"
python scripts/preflight.py
```

Preflight verifies Python, boto3, your AWS identity, your Region and your model access. When it
passes, open **`LAB_GUIDE.md`** and start at **step 1**.

Everything is run from the `episode-03-response-contract` directory.

---

## Path B — Guided setup

Same sequence, explained. Roughly ten minutes.

### 1. Get the files

```bash
git clone https://github.com/cloudbrdesign/aip-c01-labs.git
cd aip-c01-labs/episode-03-response-contract
```

**What.** Copies the repository to your machine and moves into this lab's folder.
**Why.** Every later command assumes you are in `episode-03-response-contract`.
**Expect.** A folder containing `LAB_GUIDE.md`, `requirements.txt` and a `scripts` folder.
**If it fails.** No Git? Use **Code → Download ZIP** on the repository page, unzip it, and `cd`
into the same folder. Git is a convenience here, not a requirement.

### 2. Check your Python version

```bash
python3 --version
```
```powershell
python --version    # Windows PowerShell
```

**What.** Prints the Python you have.
**Why.** The lab needs **3.9 or newer**.
**Expect.** Something like `Python 3.12.4`.
**If it fails.** `command not found` means Python is not installed or not on your PATH. Install it
from python.org. On Windows, tick **"Add Python to PATH"** in the installer. If `python` is missing
but `py` works, use `py -3` wherever these instructions say `python`.

### 3. Create a virtual environment

```bash
python3 -m venv .venv
```
```powershell
python -m venv .venv    # Windows PowerShell
```

**What.** Creates an isolated Python environment inside this lab folder, in a directory called
`.venv`.
**Why.** So the one package this lab installs lives here rather than modifying the Python your
machine uses for everything else. When you are finished you delete the folder and nothing is left
behind.
**Expect.** No output, and a new `.venv` directory.
**If it fails.** On Debian/Ubuntu you may need `sudo apt install python3-venv` first. If you get a
permissions error, you are probably somewhere you cannot write to — `cd` back into the lab folder.

### 4. Activate it

```bash
source .venv/bin/activate
```
```powershell
.venv\Scripts\Activate.ps1    # Windows PowerShell
```

**What.** Points this terminal at the environment you just created.
**Why.** Without it, the next command installs into the wrong place.
**Expect.** Your prompt gains a `(.venv)` prefix. That prefix is how you know it worked.
**If it fails.** PowerShell may refuse with an execution-policy error. Either run
`Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that window, or use
`.venv\Scripts\activate.bat` from `cmd.exe` instead.

> **Activation lasts for one terminal window.** New terminal, or reopened later — activate again
> before running anything. Preflight warns you if you forget.

### 5. Install the dependency

```bash
pip install -r requirements.txt
```

**What.** Installs `boto3`, the AWS SDK for Python.
**Why.** It is the only thing the lab needs beyond Python, and it is how the lab talks to AWS.
**Expect.** A few lines ending in `Successfully installed boto3-...`.
**If it fails.** Check `(.venv)` is in your prompt — if not, go back to step 4. Corporate networks
sometimes block PyPI; if so you will need your organisation's package mirror.

### 6. Give the SDK your AWS credentials

The lab authenticates as **you**, using **your own** AWS account.

If you have the AWS CLI, the simplest route is:

```bash
aws configure
```

which will ask for an access key, a secret key and a default Region, and store them in your home
directory.

**What.** Sets up credentials that boto3 will find automatically.
**Why.** The lab calls a real AWS service and AWS needs to know who is calling.
**Expect.** No output from the lab side; step 8 confirms it worked.
**If it fails.** Any credential mechanism boto3 understands is fine — an IAM Identity Center / SSO
session, a named profile, environment variables, or an instance/container role. If you already have
a working setup, keep it.

> **Safety, and it matters more than convenience:**
> - **Never paste access keys into a Python file.** Nothing in this lab asks you to, and nothing in
>   it ever should.
> - **Never commit credentials.** Not to this repository, not to any repository.
> - **Do not use root account credentials.** Preflight refuses to continue if it detects them.
> - **Use your own account and your own identity.** Do not copy a profile name from any
>   documentation, including ours.

If you use a named profile, tell your terminal which one:

```bash
export AWS_PROFILE=your-profile-name
```
```powershell
$env:AWS_PROFILE="your-profile-name"    # Windows PowerShell
```

### 7. Choose a Region

```bash
export AWS_REGION=us-east-1
```
```powershell
$env:AWS_REGION="us-east-1"    # Windows PowerShell
```

**What.** Tells the SDK which AWS Region to call.
**Why.** Model availability and model access are both per-Region.
**Expect.** No output.
**If it fails.** See [Region and model](#region-and-model) below.

### 8. Run preflight

```bash
python scripts/preflight.py
```

**What.** Checks Python, boto3, your AWS identity, your Region, and whether you can reach a model.
**Why.** So that if something goes wrong later you know it is the lab and not your setup. That
distinction matters in this lab more than most.
**Expect.** A short list of `[ ok ]` lines ending in *"Your environment is ready."*
**If it fails.** Each failing line prints its own fix. `TROUBLESHOOTING.md` has more under
**"Setup and environment problems."**

Preflight sends **one tiny request** to confirm model access — a couple of tokens, no resources
created. It tells you whether you can reach the model. **It tells you nothing about the lab.**

### 9. Start

Open **`LAB_GUIDE.md`** and begin at **step 1**.

---

## Region and model

**Validated configuration** — what this lab was actually built and tested against:

| | |
|---|---|
| Region | `us-east-1` |
| Model | `us.anthropic.claude-haiku-4-5-20251001-v1:0` |
| Date | 2026-08-25 |

**General requirement** — what the lab actually needs:

> **Any text model you can reach through the Bedrock `Converse` API, in a Region where you have
> access to it.**

The lab holds no model's numbers and asserts nothing about any particular model. To use a different
one, set `LAB_MODEL_ID` before running anything:

```bash
export LAB_MODEL_ID=your.model.id
```
```powershell
$env:LAB_MODEL_ID="your.model.id"    # Windows PowerShell
```

**Treat the validated configuration as a known-good starting point, not as a requirement.** If it
does not work for you, that is a matter of what your account has access to, not a defect.

**How to tell whether you have model access:** run preflight. If the model-access check passes, you
have it. If it fails, enable access for that model in the Bedrock console **in the Region you are
calling**, or pick a model you already have.

---

## IAM — the minimum

**One permission:**

| Action | Scope |
|---|---|
| `bedrock:InvokeModel` | The model you use. This one action covers the `Converse` operation |

Preflight also calls `sts:GetCallerIdentity` to confirm who you are. **That call requires no IAM
permission** — AWS allows it for any valid identity — so it adds nothing to the list above.

**`AdministratorAccess` is not required and is not recommended.** Neither is root.

**A boundary worth knowing rather than guessing:** exactly how you scope that one action depends on
what you call. A plain model id and a cross-Region inference profile id are different resources, so
a policy that names one may not cover the other. If you hit an access error after preflight
previously passed, that mismatch is the usual reason. Scope the action to the model id you actually
put in `LAB_MODEL_ID`.

---

## What this lab costs

Preflight sends one request of a couple of tokens. The lab itself sends three, of which two
generate any output at all and one of those is capped very low by construction.

**No AWS resource is created, so nothing is billed after you stop.** Bedrock's rates vary by model
and Region and change over time — if you want a number, take it from the current pricing page for
the model and Region you used.

---

## When you are finished

See `CLEANUP.md`. It is short, because there is very little to do — and it explains why that is
worth checking rather than assuming.
