from utils.llm import get_llm
import json
import re
from langsmith import traceable


@traceable(run_type="chain", name="Generate Questions")
def generate_questions(state):
    # 🔒 HARD GUARD: DO NOT regenerate MCQs if they already exist
    if state.get("mcqs"):
        return state

    llm = get_llm()

    context = state.get("teaching_context")
    if not context:
        raise RuntimeError("Cannot generate MCQs without teaching_context")

    # 1. GET DYNAMIC QUESTION COUNT (Default to 5 if not set)
    num_questions = state.get("num_questions", 5)

    # 2. PROMPT
    prompt = f"""
You are a strict examination bot. Your ONLY job is to generate a quiz based STRICTLY on the provided text.

⚠️ CRITICAL RULES:
1. **NO OUTSIDE KNOWLEDGE:** Do not ask about facts not in the text.
2. **SOLVABLE:** A student reading the text must be able to find the answer.
3. **JSON ONLY:** Output pure JSON.

Generate EXACTLY {num_questions} multiple-choice questions.

JSON SCHEMA:
[
  {{
    "question": "The question string",
    "options": ["A", "B", "C", "D"],
    "correct_answer_index": 0,
    "explanation": "Quote from text proving the answer."
  }}
]

TEXT TO TEST:
"{context}"
"""

    # ---------------------------------------------------------
    # 🔥 THE FIX IS HERE: Use .invoke() instead of llm()
    # ---------------------------------------------------------
    response = llm.invoke(prompt)
    raw = response.content.strip()

    # ---------------------------------------------------------
    # Robust JSON extraction
    # ---------------------------------------------------------
    def parse_mcqs(raw_text):
        # Case 1: Pure JSON
        try:
            return json.loads(raw_text)
        except:
            pass

        # Case 2: Markdown code blocks
        match = re.search(r"```json\s*(\[.*?\])\s*```", raw_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except:
                pass

        # Case 3: Raw list search
        match = re.search(r"\[.*\]", raw_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except:
                pass
        return None

    mcqs = parse_mcqs(raw)

    if not mcqs:
        raise RuntimeError(f"LLM failed to generate valid JSON.\nRaw Output: {raw}")

    # ---------------------------------------------------------
    # Normalization & Validation
    # ---------------------------------------------------------
    clean_mcqs = []
    for q in mcqs:
        question = q.get("question")
        options = q.get("options")
        # Handle index keys safely
        idx = q.get("correct_answer_index")
        if idx is None:
            idx = q.get("answer")

        expl = q.get("explanation", "See text for details.")

        if (question and options and isinstance(idx, int) and
                len(options) == 4 and 0 <= idx <= 3):
            clean_mcqs.append({
                "question": question,
                "options": options,
                "correct_answer_index": idx,
                "explanation": expl
            })

    # Validate count
    if len(clean_mcqs) < 1:
        raise RuntimeError(f"Invalid MCQ structure. Found {len(clean_mcqs)} questions.")

    # ✅ LOCK MCQs
    state["mcqs"] = clean_mcqs
    return state