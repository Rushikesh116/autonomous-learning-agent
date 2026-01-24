from checkpoints import CHECKPOINTS
from nodes.memory import load_memory

def define_checkpoint(state):
    idx = state["current_checkpoint"]

    if idx >= len(CHECKPOINTS):
        state["learning_complete"] = True
        return state

    cp = CHECKPOINTS[idx]
    print(f">>> STARTING CHECKPOINT {idx}: {cp['topic']}")

    state["topic"] = cp["topic"]
    state["objectives"] = cp["objectives"]
    state["retry_count"] = 0

    return state