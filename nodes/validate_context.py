def validate_context(state):
    if state["context"]:
        state["context_valid"] = True
    else:
        state["context_valid"] = False

    # increment retry counter if invalid
    if not state["context_valid"]:
        state["context_retry_count"] += 1

    return state
