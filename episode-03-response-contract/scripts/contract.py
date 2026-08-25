"""
Episode 3 lab - YOUR FILE. This is the interface you are building.

Implement handle(). It is the whole of your FM API interface: it sends one request
to the model and returns a result that the rest of your application can act on.

Your result must be able to answer the four questions the episode ends on:

    1. Is this the whole answer?
    2. If not, what kind of incomplete is it?
    3. What did we ask for?
    4. How much room did we declare?

Return whatever shape you think is right. A dict is fine. What matters is that a
caller who receives it can answer all four questions without having to know anything
about Bedrock.

Do not read ahead in the lab guide, and do not run anything until you have written
your predictions in PREDICTIONS.md.
"""


def handle(client, model_id, request):
    """Send one request and return a result answering the four questions.

    Args:
        client:    a boto3 bedrock-runtime client
        model_id:  the model id to call
        request:   one entry from lab_requests.REQUESTS - it has "messages" and
                   "inferenceConfig" keys you can pass straight to converse()

    Returns:
        your result object
    """
    raise NotImplementedError("Implement your interface here.")
