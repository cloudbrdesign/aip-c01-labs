"""Preflight - checks that your environment is ready. It does not run the lab.

    python scripts/preflight.py

Every check below is about YOUR SETUP: your Python, your dependency, your AWS
identity, your Region, and whether you can reach a model. Nothing here tells you
anything about the lab's subject.

The last check sends one very small request, because that is the only reliable way
to confirm you actually have access to the model you selected. It costs a couple of
tokens, creates nothing, and reports only whether it worked.
"""

import os
import sys

LAB_MODEL_ID = os.environ.get(
    "LAB_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0"
)
REGION = (
    os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION") or "us-east-1"
)
MIN_PYTHON = (3, 9)

_failures = []


def _describe(exc):
    """A short, safe description of a failure. Never prints identifiers or values."""
    code = (getattr(exc, "response", None) or {}).get("Error", {}).get("Code")
    return code or type(exc).__name__


def check(label, probe, fix):
    """Run one setup probe and report it.

    A preflight's job is to report problems, not to handle them, so every probe is
    guarded the same way and the guard lives here rather than in each check.
    """
    try:
        detail = probe()
    except Exception as exc:  # noqa: BLE001 - a diagnostic reports whatever went wrong
        print(f"  [FAIL] {label} - {_describe(exc)}")
        print(f"         fix: {fix}")
        _failures.append(label)
        return False
    print(f"  [ ok ] {label}{(' - ' + detail) if detail else ''}")
    return True


# --- probes. Each returns a short detail string, or raises. -------------------


def python_version():
    v = sys.version_info
    if v[:2] < MIN_PYTHON:
        raise RuntimeError(f"found {v.major}.{v.minor}, need {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+")
    return f"{v.major}.{v.minor}.{v.micro}"


def dependency():
    import boto3

    return boto3.__version__


def aws_identity():
    import boto3

    arn = boto3.client("sts").get_caller_identity()["Arn"]
    # Never print the ARN, the account id or the user name. They are yours, not ours.
    if arn.endswith(":root"):
        raise RuntimeError("these are root account credentials")
    return "resolved to a non-root identity"


def aws_region():
    if not REGION:
        raise RuntimeError("no Region set")
    return REGION


def model_access():
    import boto3

    client = boto3.client("bedrock-runtime", region_name=REGION)
    client.converse(
        modelId=LAB_MODEL_ID,
        messages=[{"role": "user", "content": [{"text": "ok"}]}],
        inferenceConfig={"maxTokens": 1},
    )
    # Deliberately returns nothing about the response itself.
    return LAB_MODEL_ID


def virtualenv_note():
    if sys.prefix == sys.base_prefix:
        print("  [warn] Virtual environment - not active")
        print("         You can continue, but SETUP.md explains why an isolated")
        print("         environment is worth having for this lab.")
    else:
        print("  [ ok ] Virtual environment - active")


def main():
    print("\nPreflight - environment only. This does not run the lab.\n")

    check("Python version", python_version,
          "install a supported Python and recreate the environment - SETUP.md step 2")
    virtualenv_note()

    ready = check("boto3 installed", dependency,
                  "activate your environment, then: pip install -r requirements.txt")
    if ready:
        ready = check("AWS credentials", aws_identity,
                      "configure credentials for your own AWS account - SETUP.md step 6. "
                      "If it reports root credentials, use an IAM user or role instead")
    if ready:
        ready = check("AWS Region", aws_region,
                      "set AWS_REGION - SETUP.md step 7")
    if ready:
        check("Model access", model_access,
              f"enable model access for {LAB_MODEL_ID} in the Bedrock console for "
              f"{REGION}, or set LAB_MODEL_ID to a model you can use - "
              "SETUP.md 'Region and model'")

    print()
    if _failures:
        print(f"Not ready yet: {len(_failures)} check(s) failed. Fix the items above "
              "and run preflight again.")
        print("These are setup problems, not lab results.\n")
        return 1
    print("Your environment is ready. Open LAB_GUIDE.md and start at step 1.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
