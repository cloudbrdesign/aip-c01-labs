# Episode 3 — The response contract

A hands-on lab for **Episode 3** of *What AIP-C01 Actually Tests*.
**[EPISODE 3 URL]** · **[SERIES PLAYLIST URL]**

You do not need to have watched the episode. You do need to be willing to commit to a prediction
before you run anything.

## What you build

A small FM API interface — the layer your application would actually call instead of calling
Amazon Bedrock directly. It sends one request and returns a result your callers can act on.

That is skill **2.5.1** of the AIP-C01 exam guide: *create FM API interfaces to address the
specific requirements of GenAI workloads*. The interesting part of that skill is not sending the
request. It is deciding what your interface tells the people who depend on it.

## What you will find out

Whether the contract you designed can represent everything the API you wrapped can actually
return. Most first attempts cannot, and finding out which part is missing — by running into it
rather than by being told — is the lab.

## Time and cost

**45–70 minutes.** Roughly half is thinking, not typing.

**Cost: effectively zero.** Three requests, two of which generate any output at all, one of those
capped at 24 output tokens by construction. **No resource of any kind is created** — no endpoint,
no store, no cache, no bucket, no log group. There is nothing to leave running and nothing to be
billed for after you close your terminal. Bedrock's rates change and vary by model and Region;
check the current rate for the model you choose if you want a figure.

## What you need

**Python 3.9+, an AWS account you control, and one IAM permission** — `bedrock:InvokeModel` on a
text model you have access to. That is the whole list.

`AdministratorAccess` is not required. Neither is Docker, Terraform, or any AWS service other than
Bedrock Runtime. **The lab creates no AWS resources**, so there is nothing to provision.

Full prerequisites — including what is *optional* and what is *not required* — are in
[`SETUP.md`](SETUP.md).

## Start here

**1. Set up your environment: [`SETUP.md`](SETUP.md).** Two paths to the same place.

| | |
|---|---|
| **Quick start** | A handful of commands, for people who set up Python projects routinely |
| **Guided setup** | The same commands, each explained, with macOS/Linux and Windows PowerShell variants and what to do when a step fails |

Both end with `python scripts/preflight.py` reporting that your environment is ready. Preflight
checks your setup only — **it tells you nothing about the lab.**

**2. Open [`LAB_GUIDE.md`](LAB_GUIDE.md) and start at step 1.** Do the steps in order. Steps 2 and 3
come before you run anything, and that ordering is the experiment rather than ceremony.

`evidence/open-after-step-7/` will spoil the lab. It says so on the directory.

## Difficulty

**The engineering problem is not simplified for anybody.** Everyone does the same experiment and
meets the same problem.

What differs is how much help you need to *reach* it. If virtual environments and AWS credentials
are familiar, take Quick start and you will be at step 1 in a couple of minutes. If they are not,
Guided setup explains every command and every likely failure. **Neither route changes the lab.**

## What is not here

- **A worked solution you can read first.** There is a reference implementation, behind the
  step-7 gate.
- **A fourth scenario about context-window exhaustion.** The episode discusses a response state
  that arises when a conversation outgrows the model's context window. **No evidence for it is
  included in this repository, because none has been captured.** It is deferred, not omitted by
  oversight, and nothing here should be read as demonstrating it. See `ARCHITECTURE.md`.

---

*Not affiliated with, endorsed by, or sponsored by Amazon Web Services. "AWS", "Amazon Web
Services" and "AWS Certified" are trademarks of Amazon.com, Inc. or its affiliates, used here only
to identify the certification this lab relates to.*
