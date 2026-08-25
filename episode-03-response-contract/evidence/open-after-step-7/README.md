# Open after step 7

| File | What it is |
|---|---|
| `RESULTS.json` | Captured output of a validated run. Read `WHAT_MATCHES.md` before comparing |
| `WHAT_MATCHES.md` | **Read this first.** What will and will not match your own run |
| `reference_contract.py` | One correct implementation. **Not the only one.** Compare behaviour, not style |

`RESULTS.json` includes a fourth entry, `client_side_demonstrator`, which is **not a lab step and
not something you are asked to run.** It exists only to show a distinction the captured evidence
needs to make: a request the SDK refused to send never reached AWS at all, and its result is not
a service response. `WHAT_MATCHES.md` explains it.
