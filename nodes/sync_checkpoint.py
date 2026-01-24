def sync_checkpoint(state):
    state["current_checkpoint"] = state["next_checkpoint"]
    return state
