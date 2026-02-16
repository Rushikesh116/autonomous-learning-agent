from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any
import bcrypt
import os

# --- 🧠 Vector Database Imports ---
import chromadb
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Import Logic
from nodes.explain_topic import explain_topic
from nodes.generate_questions import generate_questions
from nodes.evaluate_answers import evaluate_answers
from dotenv import load_dotenv

# Import DB
from database import engine, Base, get_db
from models import StudentProgress, User

load_dotenv()

# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 🚀 DEPLOYMENT CONFIGURATION
origins = [
    "http://localhost:5173",
    "https://learning-agent.vercel.app",  # Your Vercel URL
    "https://autotutor-frontend.vercel.app",
    "https://*.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 🧠 LAZY LOADING AI (Fixes Timeout) ---
# We define them as None first so the server starts FAST.
embedder = None
chroma_client = None


def get_ai_model():
    global embedder, chroma_client
    if embedder is None:
        print("⏳ Loading AI Model on first request... (This may take a few seconds)")
        embedder = SentenceTransformer('all-MiniLM-L6-v2')
        chroma_client = chromadb.Client()
        print("✅ AI Model Loaded!")
    return embedder


def calculate_relevance(context: str, question: str) -> float:
    try:
        # Load model only when needed
        model = get_ai_model()
        embeddings = model.encode([context, question])
        score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        return round(float(score), 2)
    except Exception as e:
        print(f"Vector Error: {e}")
        return 0.0


# --- 🔐 SECURITY SETUP ---

def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)


# --- 🚀 LEARNING PATH ---
CHECKPOINTS = [
    {"topic": "Introduction to Machine Learning", "objectives": ["Understand ML", "Differentiate ML vs Coding"]},
    {"topic": "Data Preprocessing", "objectives": ["Handle missing data", "Feature Scaling"]},
    {"topic": "Supervised vs Unsupervised", "objectives": ["Labeled vs Unlabeled", "Regression vs Classification"]},
    {"topic": "Linear Regression Basics", "objectives": ["Line of Best Fit", "MSE"]},
    {"topic": "Logistic Regression", "objectives": ["Sigmoid Function", "Binary Classification"]},
    {"topic": "Overfitting and Underfitting", "objectives": ["Bias-Variance Tradeoff", "Regularization"]},
    {"topic": "Model Evaluation", "objectives": ["Accuracy, Precision, Recall", "F1 Score"]},
    {"topic": "Decision Trees", "objectives": ["Splitting data", "Gini Impurity"]},
    {"topic": "K-Means Clustering", "objectives": ["Centroids", "Elbow Method"]},
    {"topic": "Neural Networks Intro", "objectives": ["Neurons", "Activation Functions"]}
]


# --- Models ---
class ExplainRequest(BaseModel):
    topic: str
    retry_count: int = 0


class QuizRequest(BaseModel):
    teaching_context: str
    num_questions: int = 5


class EvaluateRequest(BaseModel):
    mcqs: List[Dict[str, Any]]
    user_answers: List[int]
    topic: str
    student_id: str


class UserSchema(BaseModel):
    email: str
    password: str


# --- Endpoints ---

@app.get("/")
def health_check():
    return {"status": "running", "message": "AutoTutor Backend is Live!"}


@app.get("/topics")
def get_topics():
    return CHECKPOINTS


@app.get("/dashboard/{student_id}")
def get_dashboard(student_id: str, db: Session = Depends(get_db)):
    history = db.query(StudentProgress).filter(StudentProgress.student_id == student_id).all()
    mastered_topics = {record.topic for record in history if record.status == "Mastered"}

    return {
        "total_quizzes": len(history),
        "mastered_count": len(mastered_topics),
        "mastered_topics": list(mastered_topics),
        "recent_activity": [
            {"topic": r.topic, "score": r.score, "status": r.status, "date": r.timestamp.strftime("%Y-%m-%d")}
            for r in history[-5:]
        ][::-1]
    }


@app.post("/explain")
def api_explain(req: ExplainRequest):
    state = {"topic": req.topic, "retry_count": req.retry_count, "current_checkpoint": 0}
    new_state = explain_topic(state)
    return {"teaching_context": new_state["teaching_context"]}


@app.post("/quiz")
def api_quiz(req: QuizRequest):
    state = {"teaching_context": req.teaching_context, "num_questions": req.num_questions, "mcqs": None}
    try:
        new_state = generate_questions(state)
        mcqs = new_state["mcqs"]
        for q in mcqs:
            q['relevance_score'] = calculate_relevance(req.teaching_context, q['question'])
        return {"mcqs": mcqs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate")
def api_evaluate(req: EvaluateRequest, db: Session = Depends(get_db)):
    state = {"mcqs": req.mcqs, "user_answers": req.user_answers, "score": 0.0}
    new_state = evaluate_answers(state)
    score = new_state["score"]
    status = "Mastered" if score >= 70 else "Needs Review"

    try:
        new_entry = StudentProgress(student_id=req.student_id, topic=req.topic, score=score, status=status)
        db.add(new_entry)
        db.commit()
    except Exception as e:
        print(f"DB Error: {e}")

    return {"score": score, "status": status, "results": new_state.get("mcqs")}


# --- AUTH ENDPOINTS ---

@app.post("/auth/signup")
def signup(user: UserSchema, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        hashed_pw = get_password_hash(user.password)
        new_user = User(email=user.email, hashed_password=hashed_pw)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"user_id": str(new_user.id), "email": new_user.email}
    except Exception as e:
        print(f"Signup Error: {e}")
        raise HTTPException(status_code=500, detail="Signup failed")


@app.post("/auth/login")
def login(user: UserSchema, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")

    if not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid password")

    return {"user_id": str(db_user.id), "email": db_user.email}