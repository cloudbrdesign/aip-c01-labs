"""
Episode 3 lab - the three requests, and the runner.

You do not need to edit this file. Your work is in contract.py.

Each request below is a plain description of something to send to Amazon Bedrock's
Converse API. Nothing here says what any of them will do. Predicting that is step 2
of the lab guide, and you should do it before you run anything.
"""

import os

# The model the lab runs against. Override with LAB_MODEL_ID if you have access to a
# different Converse-capable model. Step 0 of the guide verifies your access.
MODEL_ID = os.environ.get(
    "LAB_MODEL_ID", "us.anthropic.claude-haiku-4-5-20251001-v1:0"
)
REGION = os.environ.get("AWS_REGION", "us-east-1")

# Deliberately far above any output ceiling any current model exposes, so that this
# lab does not depend on a specific model's number. If the service refuses it, the
# refusal itself tells you what the real ceiling is for the model you used.
ABSURDLY_LARGE_MAX_TOKENS = 999_999

REQUESTS = [
    {
        "name": "request_1",
        "messages": [
            {"role": "user", "content": [{"text": "Reply with exactly the word: acknowledged."}]}
        ],
        "inferenceConfig": {"maxTokens": 200},
    },
    {
        "name": "request_2",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "text": "Describe the process of provisioning a compliance audit "
                                "trail, in at least 400 words."
                    }
                ],
            }
        ],
        "inferenceConfig": {"maxTokens": 24},
    },
    {
        "name": "request_3",
        "messages": [
            {"role": "user", "content": [{"text": "Reply with exactly the word: acknowledged."}]}
        ],
        "inferenceConfig": {"maxTokens": ABSURDLY_LARGE_MAX_TOKENS},
    },
]


def main():
    import boto3

    from contract import handle

    client = boto3.client("bedrock-runtime", region_name=REGION)

    for request in REQUESTS:
        print(f"\n=== {request['name']} ===")
        result = handle(client, MODEL_ID, request)
        print(result)


if __name__ == "__main__":
    main()
