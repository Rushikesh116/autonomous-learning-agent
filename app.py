import streamlit as st
from checkpoints import CHECKPOINTS
from nodes.explain_topic import explain_topic
from nodes.generate_questions import generate_questions
from nodes.evaluate_answers import evaluate_answers
from dotenv import load_dotenv

# 1. LOAD ENV VARS (Critical for Tracing)
load_dotenv()

# ---------------------------------
# 🎨 PAGE CONFIGURATION
# ---------------------------------
st.set_page_config(
    page_title="Autonomous Learning Agent",
    page_icon="🧠",
    layout="wide",  # Widescreen mode for better readability
    initial_sidebar_state="expanded"
)

# ---------------------------------
# 💅 CUSTOM CSS STYLING
# ---------------------------------
st.markdown("""
<style>
    /* Main Title Styling */
    .main-title {
        font-size: 3rem;
        color: #4A90E2;
        text-align: center;
        margin-bottom: 0px;
    }
    .sub-title {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 30px;
    }
    /* Question Card Styling */
    .question-card {
        background-color: #f9f9f9;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        border-left: 5px solid #4A90E2;
    }
    /* Success/Error Highlights for Results */
    .correct-ans {
        background-color: #d4edda;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #28a745;
        margin-bottom: 10px;
    }
    .wrong-ans {
        background-color: #f8d7da;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #dc3545;
        margin-bottom: 10px;
    }
    .insight-box {
        background-color: #e2e3e5;
        padding: 10px;
        border-radius: 5px;
        font-style: italic;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------
# SESSION STATE INITIALIZATION
# ---------------------------------
if "phase" not in st.session_state:
    st.session_state.phase = "select"
if "state" not in st.session_state:
    st.session_state.state = {}

# ---------------------------------
# 🧠 SIDEBAR: NAVIGATION & SETTINGS
# ---------------------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712009.png", width=80)
    st.title("Settings")

    # Only show controls if in 'select' phase to prevent changing mid-quiz
    disabled = st.session_state.phase != "select"

    checkpoint_index = st.selectbox(
        "📚 Learning Topic:",
        options=list(range(len(CHECKPOINTS))),
        format_func=lambda i: CHECKPOINTS[i]["topic"],
        disabled=disabled
    )

    num_questions = st.slider(
        "❓ Quiz Length:",
        min_value=3, max_value=10, value=5,
        disabled=disabled
    )

    st.markdown("---")
    st.markdown(f"**Current Phase:** `{st.session_state.phase.upper()}`")

    # Reset Button always available
    if st.button("🔄 Reset App", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# ---------------------------------
# PHASE 1: HOME / SELECT
# ---------------------------------
if st.session_state.phase == "select":
    st.markdown('<h1 class="main-title">🧠 Autonomous Learning Agent</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">Your AI-powered personalized tutor using Feynman Pedagogy</p>',
                unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info(f"**Selected Topic:** {CHECKPOINTS[checkpoint_index]['topic']}")

        if st.button("🚀 Start Learning Journey", type="primary", use_container_width=True):
            st.session_state.state = {
                "current_checkpoint": checkpoint_index,
                "retry_count": 0,
                "score": 0.0,
                "topic": CHECKPOINTS[checkpoint_index]["topic"],
                "teaching_context": "",
                "mcqs": None,
                "user_answers": [],
                "num_questions": num_questions
            }
            st.session_state.phase = "learn"
            st.rerun()

# ---------------------------------
# PHASE 2: EXPLANATION (Standard)
# ---------------------------------
elif st.session_state.phase == "learn":
    # Header with nice spacing
    c1, c2 = st.columns([8, 1])
    c1.title(f"📘 {st.session_state.state['topic']}")

    # Content Generation
    if not st.session_state.state.get("teaching_context"):
        with st.status("🧠 Agent is preparing your lesson...", expanded=True) as status:
            st.write("Searching knowledge base...")
            explain_topic(st.session_state.state)
            status.update(label="✅ Lesson Ready!", state="complete", expanded=False)

    # Display Content
    with st.container():
        st.markdown(st.session_state.state.get("teaching_context", "Error loading context."))

    st.markdown("---")

    # Centered 'Take Quiz' button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📝 Ready for Quiz?", type="primary", use_container_width=True):
            with st.spinner("🤖 Generating custom questions..."):
                generate_questions(st.session_state.state)

            if not st.session_state.state.get("mcqs"):
                st.error("Failed to generate questions. Please try again.")
            else:
                st.session_state.phase = "quiz"
                st.rerun()

# ---------------------------------
# PHASE 3: QUIZ
# ---------------------------------
elif st.session_state.phase == "quiz":
    st.title("📝 Knowledge Check")
    st.caption("Select the best answer for each question below.")
    st.progress(0, text="Quiz in progress...")

    questions = st.session_state.state.get("mcqs", [])

    with st.form("quiz_form"):
        answers = []
        for i, q in enumerate(questions):
            st.markdown(f"#### Q{i + 1}. {q['question']}")

            opts = q.get("options", [])
            choice = st.radio(
                label=f"Options for Q{i + 1}",
                options=list(range(len(opts))),
                format_func=lambda idx: opts[idx],
                key=f"q_{i}",
                label_visibility="collapsed"
            )
            answers.append(choice)
            st.markdown("---")

        submitted = st.form_submit_button("✅ Submit Answers", type="primary", use_container_width=True)

        if submitted:
            st.session_state.state["user_answers"] = answers
            st.session_state.phase = "evaluate"
            st.rerun()

# ---------------------------------
# PHASE 4: EVALUATION & RESULTS
# ---------------------------------
elif st.session_state.phase == "evaluate":
    evaluate_answers(st.session_state.state)
    score = st.session_state.state.get("score", 0.0)

    st.title("📊 Results Dashboard")

    # Metric Columns
    col1, col2, col3 = st.columns(3)
    col1.metric("Score", f"{score:.0f}%")
    col2.metric("Status", "Mastered" if score >= 70 else "Needs Review")
    col3.metric("Questions", len(st.session_state.state["mcqs"]))

    # Color-coded Progress Bar
    bar_color = "green" if score >= 70 else "red"
    st.progress(min(score / 100, 1.0))

    st.divider()
    st.subheader("🧐 Detailed Review")

    questions = st.session_state.state.get("mcqs", [])
    user_answers = st.session_state.state.get("user_answers", [])

    # Render Custom HTML Cards for Feedback
    for i, (q, user_ans) in enumerate(zip(questions, user_answers)):
        correct_idx = q.get("correct_answer_index", 0)
        options = q.get("options", [])
        explanation = q.get("explanation", "No explanation provided.")

        # Safety check for indices
        if user_ans < len(options):
            user_text = options[user_ans]
        else:
            user_text = "Invalid Selection"

        correct_text = options[correct_idx]

        with st.expander(f"Q{i + 1}: {q['question']}", expanded=True):
            if user_ans == correct_idx:
                st.markdown(f"""
                <div class="correct-ans">
                    <b>✅ Correct!</b> You chose: {user_text}
                </div>
                <div class="insight-box">💡 Insight: {explanation}</div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="wrong-ans">
                    <b>❌ Incorrect.</b> You chose: {user_text}<br>
                    <b>👉 Correct Answer:</b> {correct_text}
                </div>
                <div class="insight-box">💡 Insight: {explanation}</div>
                """, unsafe_allow_html=True)

    st.divider()

    # --- LOGIC BRANCHING ---
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if score >= 70:
            st.balloons()
            st.success("🎉 Checkpoint Mastered!")
            next_idx = st.session_state.state["current_checkpoint"] + 1

            if next_idx < len(CHECKPOINTS):
                if st.button("⏭️ Next Topic", type="primary", use_container_width=True):
                    st.session_state.state.update({
                        "current_checkpoint": next_idx,
                        "score": 0.0,
                        "teaching_context": "",
                        "mcqs": None,
                        "user_answers": [],
                        "topic": CHECKPOINTS[next_idx]["topic"]
                    })
                    st.session_state.phase = "learn"
                    st.rerun()
            else:
                st.success("🎓 You have completed the entire learning path!")
                if st.button("🏠 Return Home", use_container_width=True):
                    st.session_state.phase = "select"
                    st.rerun()
        else:
            st.error("⚠️ Score below 70%. Let's simplify this.")
            if st.button("💡 Simplify (Feynman Technique)", type="primary", use_container_width=True):
                st.session_state.phase = "feynman"
                st.rerun()

# ---------------------------------
# PHASE 5: FEYNMAN REMEDIATION
# ---------------------------------
elif st.session_state.phase == "feynman":
    st.title("💡 Simplified Explanation")
    st.caption("Feynman Technique Active: Using analogies and simple terms.")

    # Logic to trigger simplification
    if "feynman_context" not in st.session_state.state:
        with st.status("Thinking like a master teacher...") as status:
            st.session_state.state["retry_count"] += 1
            # Explain topic will see retry_count > 0 and use Feynman Mode
            explain_topic(st.session_state.state)
            st.session_state.state["feynman_context"] = st.session_state.state["teaching_context"]
            status.update(label="Simplification Complete!", state="complete")

    # Display Content
    st.markdown(st.session_state.state.get("feynman_context", "No context available."))

    st.divider()

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("📝 Take Quiz", type="primary", use_container_width=True):
            st.session_state.state["mcqs"] = None

            # Generate NEW questions based on FEYNMAN context
            with st.spinner("Generating new questions..."):
                generate_questions(st.session_state.state)

            if st.session_state.state.get("mcqs"):
                st.session_state.phase = "quiz"
                st.rerun()
            else:
                st.error("Error generating questions.")