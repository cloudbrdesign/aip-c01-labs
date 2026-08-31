# One valid design

`one_valid_design.json` satisfies every rule the checker enforces.

**It is one valid design, not the valid design.** If yours is different and the checker accepts it,
yours is not a worse answer — it is a different instrument, and it measures different things.

`WHY_THIS_IS_LEGAL.md` explains what makes it legal, what measurement intent it represents, what
else would also have been legal, and what its legality does not establish.

You can run the checker against it:

```bash
python3 scripts/check_design.py --design evidence/open-after-step-5/one_valid_design.json
```
