from nodes.memory import load_memory, save_memory
from langsmith import traceable  # <--- IMPORT THIS

@traceable(run_type="chain", name="Generate Questions")

def evaluate_answers(state):
    mcqs = state.get("mcqs", [])
    user_answers = state.get("user_answers", [])

    if not mcqs or not user_answers:
        state["score"] = 0.0
        return state

    correct = 0

    for i, q in enumerate(mcqs):
        # FIX: Try to get 'correct_answer_index' first, fall back to 'answer'
        correct_idx = q.get("correct_answer_index")
        if correct_idx is None:
            correct_idx = q.get("answer")

        # Check against user answer
        if i < len(user_answers) and user_answers[i] == correct_idx:
            correct += 1

    # Calculate score dynamically based on total questions
    if len(mcqs) > 0:
        state["score"] = (correct / len(mcqs)) * 100
    else:
        state["score"] = 0.0

    return state