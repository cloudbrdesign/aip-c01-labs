# aip-c01-labs

Hands-on engineering labs for the **What AIP-C01 Actually Tests** course.

Each lab is small, cheap, and built around a single thing an AWS GenAI service actually does at
one of its edges. They are engineering exercises rather than click-throughs: you build something,
predict what it will do, run it, and find out where your model of the system was wrong.

## Labs

| Lab | Episode | What you build |
|---|---|---|
| [`episode-03-response-contract/`](episode-03-response-contract/) | Episode 3 | An FM API interface, and a contract that can represent everything the API it wraps can return |
| [`episode-05-measurement-design/`](episode-05-measurement-design/) | Episode 5 | A measurement instrument — what you evaluate, on what, and by what rule — checked against constraints AWS documents. **Local, $0, no AWS account.** |
| [`episode-06-comparability-review/`](episode-06-comparability-review/) | Episode 6 | An engineering review of two finished measurements against a stated comparison claim — what the artifacts establish, what they do not, and which differences bear on the claim. **Local, $0, no AWS account.** |

## What these labs are like

- **Cheap.** Costs are stated per lab. Where a lab creates no resource at all, it says so and
  explains why that claim is worth checking.
- **Yours to run.** Where a lab touches AWS it uses your account, your credentials, your Region and
  your model — never ours, and never any private infrastructure. Some labs touch AWS not at all.
- **Cleaned up.** Every lab states what it creates and how to confirm nothing was left behind.
- **Honest about their edges.** Where something is unverified or deliberately out of scope, the
  lab says so instead of implying coverage it does not have.

## Advanced concepts; accessible execution

The difficulty in these labs comes from the engineering problem, never from guessing how to run
them. Setup instructions explain every command, cover macOS, Linux and Windows, and say what to do
when a step fails — without simplifying the engineering for anyone.

Every lab ships a **preflight check** that confirms your environment is ready before you begin, so a
missing package or an unset Region never gets mistaken for a result.

## Before you start any lab

Read that lab's `README.md` first. It states time, cost, prerequisites and where to begin, and
points at a `SETUP.md` where the lab needs one. Labs are meant to be done in step order — several depend on you
committing to a prediction before you run anything, and reading ahead removes the only interesting
part.

## Licence

Licensed under the **Apache License, Version 2.0**. See [`LICENSE`](LICENSE) for the full text.

---

*Independent educational project. Not affiliated with, endorsed by, or sponsored by Amazon Web
Services. "AWS", "Amazon Web Services" and "AWS Certified" are trademarks of Amazon.com, Inc. or
its affiliates, used here only to identify the certification these labs relate to.*
