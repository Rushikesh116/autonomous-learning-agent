from checkpoints import CHECKPOINTS
from langsmith import traceable
from utils.llm import get_llm


@traceable(run_type="chain", name="Explain Topic")
def explain_topic(state):
    # ---------------------------------------------------------
    # 🔧 BUG FIX: Prioritize the 'topic' string if provided
    # ---------------------------------------------------------
    topic = state.get("topic")

    # If no topic string was passed, look it up by index
    if not topic:
        idx = state.get("current_checkpoint", 0)
        if idx < len(CHECKPOINTS):
            topic = CHECKPOINTS[idx]["topic"]
        else:
            topic = "General Machine Learning"
        state["topic"] = topic

    # 2. Check for Retry (Feynman Mode)
    retry_count = state.get("retry_count", 0)
    llm = get_llm()

    # ---------------------------------------------------------
    # SCENARIO A: FEYNMAN SIMPLIFICATION (Retry > 0)
    # ---------------------------------------------------------
    if retry_count > 0:
        print(f"🔹 FEYNMAN MODE: Explaining {topic}")
        prompt = f"""
        You are Richard Feynman. Explain "{topic}" to a student who is struggling.

        GUIDELINES:
        1. **Simplify Ruthlessly:** Use clear, simple English. Avoid jargon.
        2. **Use Analogies:** Explain the concept using a real-world comparison (cooking, sports, driving).
        3. **Tone:** Professional but accessible.

        FORMAT (Use Markdown):
        # 💡 {topic} (Simplified)

        ## 1. The Core Idea
        [Explain it simply, as if talking to a smart beginner.]

        ## 2. A Real-World Analogy
        [Your analogy here]

        ## 3. Why It Matters
        [1 sentence takeaway]
        
        add more information if needed
        """

    # ---------------------------------------------------------
    # SCENARIO B: STANDARD EXPLANATION (First Attempt)
    # ---------------------------------------------------------
    else:
        print(f"🔹 STANDARD MODE: Explaining {topic}")
        prompt = f"""
        You are an expert professor designing a clear, structured lesson on "{topic}".
        Your goal is to provide a comprehensive yet concise overview.

        GUIDELINES:
        1. **Structure:** Use clear headings and bullet points.
        2. **Clarity:** Define key terms immediately.
        3. **Depth:** Cover the "What", "How", and "Why".

        FORMAT (Use Markdown):
        # 📘 Topic: {topic}

        ## 1. Core Definition
        [Clear definition]

        ## 2. Key Concepts
        * **[Concept 1]:** [Explanation]
        * **[Concept 2]:** [Explanation]
        * **[Concept 3]:** [Explanation]

        ## 3. Real-World Application
        [A concrete example of how this is used in real life]

        ## 4. Summary
        [A powerful closing sentence]
        
        add more information if needed
        """

    try:
        response = llm.invoke(prompt)
        state["teaching_context"] = response.content
    except Exception as e:
        print(f"⚠️ Error in Explain Topic: {e}")
        state["teaching_context"] = f"Error generating explanation for {topic}. Please retry."

    return state