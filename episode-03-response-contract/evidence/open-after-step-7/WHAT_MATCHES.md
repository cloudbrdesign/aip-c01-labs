# Evidence — what will and will not match your own run

Captured from two independent validation passes against
`us.anthropic.claude-haiku-4-5-20251001-v1:0` in `us-east-1`.
**No account id, principal ARN, credential or request id is recorded in any file here.**

## What WILL match

- **The state of every request.** `ANSWERED` / `REJECTED` / `NOT_SENT` were identical across
  both passes and will be identical for you.
- **The termination signal** where one exists: `end_turn` for request 1, `max_tokens` for
  request 2, **and none at all for request 3**.
- **Which layer each request reached** — `reached_service` and `inference_ran`.
- **`inputTokens`** — the input is fixed, and tokenization is deterministic.

## What will NOT match, and must not be treated as the result

- **The generated text.** Generation is not deterministic. Across our two passes the same
  request 2 produced *"…A Comprehensive Process\n\n## Introduction\n\nProvisioning a compliance"*
  and *"…A Comprehensive Process\n\n## Overview\n\nA compliance audit trail is"*. **Identical
  state, different words.** If you are comparing text, you are measuring the wrong thing.
- **`outputTokens` for request 1**, which depends on what the model chose to say.
- **`latencyMs`**.
- **The specific ceiling named in request 3's rejection message.** Ours says one number for the
  model we used. **It is a fact about that model on that date, not a fact about Bedrock.** If you
  run a different model you should expect a different number — and the message will tell you
  what it is, which is the point.

## The three layers, and why the evidence separates them

Every captured result records `reached_service` and `inference_ran`, because *"the request
failed"* covers three different things that need different handling:

| | `reached_service` | `inference_ran` | Is there a termination signal? |
|---|---|---|---|
| **NOT_SENT** — your SDK refused the call | `false` | `false` | No, and **AWS never saw this request** |
| **REJECTED** — AWS refused it | `true` | `false` | **No** |
| **ANSWERED** — inference ran | `true` | `true` | **Yes** |

**`client_side_demonstrator` is not a lab step.** It exists only to make the first row visible.
Its result comes from the AWS SDK's own parameter validation and **never reached AWS**. It must
never be described, quoted or captured as a Bedrock service response.

## Files

| File | Contents |
|---|---|
| `RESULTS.json` | Captured output of a validated run |
| `reference_contract.py` | One correct implementation. Not the only one — compare behaviour, not style |

This lab was validated over **two** independent runs, the second from a completely torn-down
state, to prove the sequence reproduces rather than merely repeats. **One run's output is
published**; the second differed only in the generated prose, exactly as described above. That
difference is the reason this page exists.
