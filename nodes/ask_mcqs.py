from langsmith import traceable  # <--- IMPORT THIS

@traceable(run_type="chain", name="Generate Questions")
def ask_mcqs(state):
    mcqs = state["mcqs"]
    user_answers = []
    score = 0

    print("\n--- Answer the following MCQs ---\n")

    for i, q in enumerate(mcqs):
        print(f"Q{i+1}. {q['question']}")
        for idx, opt in enumerate(q["options"]):
            print(f"  {idx}. {opt}")

        while True:
            user_input = input("Your answer (0-3): ").strip()
            if user_input.isdigit() and int(user_input) in range(len(q["options"])):
                ans = int(user_input)
                break
            print("❌ Invalid input. Enter a number like 0, 1, 2, or 3.")

        user_answers.append(ans)

        if ans == q["answer"]:
            score += 1

    state["user_answers"] = user_answers
    state["score"] = (score / len(mcqs)) * 100


    return state
