"""REFERENCE - the corrected contract.

The correction the learner makes after request 3 is the assessed outcome of this lab.
This is the reference form, not the only acceptable one. What any acceptable answer
must do is represent an outcome for which there is no response object at all, and
therefore no termination signal to branch on.

Three layers are kept distinct, because they are distinct:

    NOT_SENT   - the SDK refused the call. Nothing reached AWS. This is not a
                 service response and must never be reported as one.
    REJECTED   - the request reached AWS and AWS refused it. Inference did not run,
                 so there is no response, no termination signal and no usage.
    ANSWERED   - inference ran and returned the normal response contract.

Only the third has a termination signal. That is the whole point.
"""

from botocore.exceptions import ClientError, ParamValidationError

# Documented Converse stopReason values, mapped to what a caller actually needs to
# know. Values not listed here are still returned verbatim in "termination_signal";
# an interface should never silently collapse a signal it does not recognise.
_COMPLETE = {"end_turn", "stop_sequence"}
_MEANING = {
    "end_turn": "the model finished",
    "stop_sequence": "the model hit a stop sequence you configured",
    "max_tokens": "generation reached an output ceiling - yours or the model's",
    "model_context_window_exceeded": "generation stopped at the context window",
}


def handle(client, model_id, request):
    declared = request.get("inferenceConfig", {}).get("maxTokens")
    base = {
        "request": request["name"],
        "model_id": model_id,
        "declared_max_tokens": declared,
    }

    try:
        response = client.converse(
            modelId=model_id,
            messages=request["messages"],
            inferenceConfig=request["inferenceConfig"],
        )
    except ParamValidationError as exc:
        return {
            **base,
            "reached_service": False,
            "inference_ran": False,
            "complete": False,
            "state": "NOT_SENT",
            "termination_signal": None,
            "text": None,
            "usage": None,
            "detail": f"client-side parameter validation: {exc}",
        }
    except ClientError as exc:
        error = exc.response.get("Error", {})
        meta = exc.response.get("ResponseMetadata", {})
        return {
            **base,
            "reached_service": True,
            "inference_ran": False,
            "complete": False,
            "state": "REJECTED",
            "termination_signal": None,
            "text": None,
            "usage": None,
            "detail": f"{error.get('Code')} (HTTP {meta.get('HTTPStatusCode')}): {error.get('Message')}",
        }

    signal = response["stopReason"]
    return {
        **base,
        "reached_service": True,
        "inference_ran": True,
        "complete": signal in _COMPLETE,
        "state": "ANSWERED",
        "termination_signal": signal,
        "text": response["output"]["message"]["content"][0]["text"],
        "usage": response["usage"],
        "detail": _MEANING.get(signal, "unrecognised termination signal - do not assume"),
    }
