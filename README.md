# aip-c01-labs

Hands-on engineering labs for the **What AIP-C01 Actually Tests** course.

Each lab is small, cheap, and built around a single thing an AWS GenAI service actually does at
one of its edges. They are engineering exercises rather than click-throughs: you build something,
predict what it will do, run it, and find out where your model of the system was wrong.

## Labs

| Lab | Episode | What you build |
|---|---|---|
| [`episode-03-response-contract/`](episode-03-response-contract/) | Episode 3 | An FM API interface, and a contract that can represent everything the API it wraps can return |

## What these labs are like

- **Cheap.** Costs are stated per lab. Where a lab creates no resource at all, it says so and
  explains why that claim is worth checking.
- **Yours to run.** Your account, your credentials, your Region, your model. No lab depends on
  our account, our resource ids, or any private infrastructure.
- **Cleaned up.** Every lab states what it creates and how to confirm nothing was left behind.
- **Honest about their edges.** Where something is unverified or deliberately out of scope, the
  lab says so instead of implying coverage it does not have.

## Advanced concepts; accessible execution

The difficulty in these labs comes from the engineering problem, never from guessing how to run
them. Each lab ships a **Quick start** for people who set up Python projects routinely and a
**Guided setup** that explains every command, covers macOS, Linux and Windows, and says what to do
when a step fails. Both routes reach the same experiment — the engineering is not simplified for
anyone.

Each lab also ships a **preflight check** that confirms your environment is ready before you begin,
so a missing package or an unset Region never gets mistaken for a result.

## Before you start any lab

Read that lab's `README.md` first, then its `SETUP.md`. Between them they state time, cost,
prerequisites and where to begin. Labs are meant to be done in step order — several depend on you
committing to a prediction before you run anything, and reading ahead removes the only interesting
part.

## Licence

Licensed under the **Apache License, Version 2.0**. See [`LICENSE`](LICENSE) for the full text.

---

*Independent educational project. Not affiliated with, endorsed by, or sponsored by Amazon Web
Services. "AWS", "Amazon Web Services" and "AWS Certified" are trademarks of Amazon.com, Inc. or
its affiliates, used here only to identify the certification these labs relate to.*
