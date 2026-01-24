from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any

# Import your existing logic
from nodes.explain_topic import explain_topic
from nodes.generate_questions import generate_questions
from nodes.evaluate_answers import evaluate_answers
from checkpoints import CHECKPOINTS
from dotenv import load_dotenv

# Import DB modules
from database import engine, Base, get_db
from models import StudentProgress

load_dotenv()

# Create Tables automatically on startup if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 🔓 Enable CORS (Allows React on port 5173 to talk to Python on port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Data Models (Validation) ---
class ExplainRequest(BaseModel):
    topic: str
    retry_count: int = 0


class QuizRequest(BaseModel):
    teaching_context: str
    num_questions: int = 5


class EvaluateRequest(BaseModel):
    mcqs: List[Dict[str, Any]]
    user_answers: List[int]
    topic: str  # <--- NEW: Required to save progress
    student_id: str = "guest"  # <--- NEW: Default user ID


# --- Endpoints ---

@app.get("/topics")
def get_topics():
    return CHECKPOINTS


@app.get("/dashboard/{student_id}")
def get_dashboard(student_id: str, db: Session = Depends(get_db)):
    """
    Returns statistics for the student dashboard:
    - Total quizzes taken
    - Number of unique topics mastered
    - Recent activity log
    """
    # 1. Get all attempts by this student
    history = db.query(StudentProgress).filter(StudentProgress.student_id == student_id).all()

    # 2. Calculate Stats
    total_quizzes = len(history)

    # Find unique topics that have at least one "Mastered" entry
    mastered_topics = set()
    for record in history:
        if record.status == "Mastered":
            mastered_topics.add(record.topic)

    # 3. Return JSON
    return {
        "total_quizzes": total_quizzes,
        "mastered_count": len(mastered_topics),
        "mastered_topics": list(mastered_topics),
        "recent_activity": [
            {
                "topic": r.topic,
                "score": r.score,
                "status": r.status,
                "date": r.timestamp.strftime("%Y-%m-%d %H:%M")
            }
            for r in history[-5:]  # Show last 5 activities
        ][::-1]  # Reverse to show newest first
    }


@app.post("/explain")
def api_explain(req: ExplainRequest):
    state = {
        "topic": req.topic,
        "retry_count": req.retry_count,
        "current_checkpoint": 0
    }
    new_state = explain_topic(state)
    return {"teaching_context": new_state["teaching_context"]}


@app.post("/quiz")
def api_quiz(req: QuizRequest):
    state = {
        "teaching_context": req.teaching_context,
        "num_questions": req.num_questions,
        "mcqs": None
    }
    try:
        new_state = generate_questions(state)
        return {"mcqs": new_state["mcqs"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate")
def api_evaluate(req: EvaluateRequest, db: Session = Depends(get_db)):
    # 1. Calculate Score (Existing Logic)
    state = {
        "mcqs": req.mcqs,
        "user_answers": req.user_answers,
        "score": 0.0
    }
    new_state = evaluate_answers(state)
    final_score = new_state["score"]
    status = "Mastered" if final_score >= 70 else "Needs Review"

    # 2. Save to PostgreSQL (New Logic)
    try:
        new_entry = StudentProgress(
            student_id=req.student_id,
            topic=req.topic,
            score=final_score,
            status=status
        )
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
    except Exception as e:
        print(f"Database Error: {e}")
        # We continue even if DB fails so user sees their score

    return {
        "score": final_score,
        "status": status,
        "results": new_state.get("mcqs")
    }