# Scenario — the handover summariser

You work on an internal tool for a customer support team.

When a shift ends, open tickets are handed to the next agent. Reading a long thread takes time,
so the team built a feature: the model reads the whole ticket thread and writes a short handover
note saying **what happened, what was done, and what is still outstanding**.

It has been running for three weeks. Agents are using it. Nobody has measured it.

Your job this week is to **measure it**.

Ten real threads have been prepared for you, with the identifying details removed. They cover
bugs, billing, an account limit, a compliance question, an integration failure, an escalation,
a capability question, an email deliverability problem, and a performance complaint.

---

## What people have said about it in the team channel

These are the things colleagues have actually said. They are not requirements, and they do not
agree with each other. Some of them describe different concerns; some describe the same concern
in different words.

> "It reads well but I don't trust it."

> "Twice now it's mentioned a refund that wasn't in the thread."

> "It leaves out the thing the customer is actually waiting for."

> "It's fine, it's just too long to skim at 6am."

> "It said the ticket was resolved. It wasn't resolved."

> "It doesn't tell you who to chase."

---

## Before you touch any configuration

**Write one sentence: what do you want to know about this feature's output?**

Not what you want the feature to do. What you want to *know* about what it produces.

Write it down before you read `LAB_GUIDE.md`. You will be asked to compare it with what you
built, at the end, and it only works if you wrote it first.

---

## What this scenario deliberately does not include

- No target number, and nothing to reach.
- No decision waiting on your answer — nobody is asking whether to keep or replace anything.
- No second model to weigh this one against.
- No domain knowledge beyond reading a support ticket.
- No arithmetic.

**You are building the instrument. Nothing else.**
