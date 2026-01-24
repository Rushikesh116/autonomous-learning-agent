from utils.llm import get_llm
from langsmith import traceable  # <--- IMPORT THIS

@traceable(run_type="chain", name="Generate Questions")
def feynman_teach(state):
    llm = get_llm()
    topic = state["topic"]
    prev = state["teaching_context"]

    wrong_qs = [
        q for i, q in enumerate(state["mcqs"])
        if state["user_answers"][i] != q["answer"]
    ]

    prompt = f"""
    You are a Feynman-style teacher.

    The student misunderstood the following questions:
    {wrong_qs}

    Re-explain "{state['topic']}" very simply:
    - Use analogy
    - Address the misunderstanding
    - Assume the student is a beginner
    - Do NOT repeat previous explanation
    """

    simplified = llm(prompt)

    # 🔒 Feynman fallback
    if len(simplified.split()) < 20:
        simplified = (
            f"Let’s explain {topic} very simply. "
            f"Imagine teaching a child by showing examples instead of rules. "
            f"This topic is about how computers learn in that simple way."
        )

    state["teaching_context"] = simplified

    print("\n--- FEYNMAN EXPLANATION ---")
    print(simplified)
    print("--------------------------\n")

    return state
