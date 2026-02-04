from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Dict, Any

# --- 🧠 NEW: Vector Database & AI Imports ---
import chromadb
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Import your existing logic
from nodes.explain_topic import explain_topic
from nodes.generate_questions import generate_questions
from nodes.evaluate_answers import evaluate_answers
from dotenv import load_dotenv

# Import DB modules
from database import engine, Base, get_db
from models import StudentProgress

load_dotenv()

# Create Tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI()

# 🔓 Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 🤖 INITIALIZE VECTOR AI ---
print("⏳ Loading AI Embedding Model... (This might take a moment)")
embedder = SentenceTransformer('all-MiniLM-L6-v2')
chroma_client = chromadb.Client()  # In-memory vector DB
print("✅ AI Model Loaded!")


def calculate_relevance(context: str, question: str) -> float:
    """
    Uses Vector Embeddings to mathematically calculate how relevant
    a question is to the teaching context.
    Returns: Score between 0.0 (Unrelated) and 1.0 (Perfect Match)
    """
    try:
        # 1. Turn text into numbers (Vectors)
        embeddings = embedder.encode([context, question])

        # 2. Calculate Cosine Similarity
        # (Reshape is needed because sklearn expects 2D arrays)
        score = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        return round(float(score), 2)
    except Exception as e:
        print(f"⚠️ Vector Error: {e}")
        return 0.0


# --- 🚀 THE FULL LEARNING PATH (10 Levels) ---
CHECKPOINTS = [
    {
        "topic": "Introduction to Machine Learning",
        "objectives": [
            "Understand what Machine Learning is",
            "Differentiate ML from traditional programming",
            "Identify real-world applications of ML"
        ]
    },
    {
        "topic": "Data Preprocessing & Feature Engineering",
        "objectives": [
            "Handle missing data and outliers",
            "Understand Feature Scaling (Normalization vs Standardization)",
            "Convert categorical data (One-Hot Encoding)"
        ]
    },
    {
        "topic": "Supervised vs Unsupervised Learning",
        "objectives": [
            "Define Supervised Learning (Labeled Data)",
            "Define Unsupervised Learning (Unlabeled Data)",
            "Compare Regression vs Classification tasks"
        ]
    },
    {
        "topic": "Linear Regression Basics",
        "objectives": [
            "Understand the Line of Best Fit",
            "Explain Dependent and Independent variables",
            "Interpret Mean Squared Error (MSE)"
        ]
    },
    {
        "topic": "Logistic Regression for Classification",
        "objectives": [
            "Understand the Sigmoid Function",
            "Differentiate between Binary and Multiclass classification",
            "Interpret a Confusion Matrix"
        ]
    },
    {
        "topic": "Overfitting and Underfitting",
        "objectives": [
            "Define Overfitting (High Variance)",
            "Define Underfitting (High Bias)",
            "Explain the Bias-Variance Tradeoff"
        ]
    },
    {
        "topic": "Model Evaluation Metrics",
        "objectives": [
            "Calculate Accuracy, Precision, and Recall",
            "Understand the F1 Score",
            "Explain ROC Curves and AUC"
        ]
    },
    {
        "topic": "Decision Trees & Random Forests",
        "objectives": [
            "Understand how Decision Trees split data",
            "Explain Ensemble Learning",
            "Differentiate between Bagging and Boosting"
        ]
    },
    {
        "topic": "K-Means Clustering",
        "objectives": [
            "Understand Centroids and Clusters",
            "Explain the Elbow Method",
            "Identify use cases for Clustering"
        ]
    },
    {
        "topic": "Introduction to Neural Networks",
        "objectives": [
            "Understand Neurons and Layers",
            "Explain Activation Functions (ReLU, Sigmoid)",
            "Define Forward and Backward Propagation"
        ]
    }
]


# --- Data Models ---
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
    student_id: str = "guest"


# --- Endpoints ---

@app.get("/topics")
def get_topics():
    return CHECKPOINTS


@app.get("/dashboard/{student_id}")
def get_dashboard(student_id: str, db: Session = Depends(get_db)):
    history = db.query(StudentProgress).filter(StudentProgress.student_id == student_id).all()
    total_quizzes = len(history)
    mastered_topics = set()
    for record in history:
        if record.status == "Mastered":
            mastered_topics.add(record.topic)

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
            for r in history[-5:]
        ][::-1]
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
        # 1. Generate Questions using Groq (LLM)
        new_state = generate_questions(state)
        generated_mcqs = new_state["mcqs"]

        # 2. 🛡️ VERIFY with Vector AI
        validated_mcqs = []
        print(f"\n🔍 Validating {len(generated_mcqs)} questions with Vector Embeddings...")

        for q in generated_mcqs:
            # Calculate score (0 to 1)
            rel_score = calculate_relevance(req.teaching_context, q['question'])
            print(f"   Question: {q['question'][:30]}... | Score: {rel_score}")

            # Add score to the question object (so Frontend can see it if needed)
            q['relevance_score'] = rel_score

            # Logic: You could filter here (e.g., if rel_score > 0.3)
            # For now, we return all but log the scores.
            validated_mcqs.append(q)

        return {"mcqs": validated_mcqs}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate")
def api_evaluate(req: EvaluateRequest, db: Session = Depends(get_db)):
    state = {
        "mcqs": req.mcqs,
        "user_answers": req.user_answers,
        "score": 0.0
    }
    new_state = evaluate_answers(state)
    final_score = new_state["score"]
    status = "Mastered" if final_score >= 70 else "Needs Review"

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

    return {
        "score": final_score,
        "status": status,
        "results": new_state.get("mcqs")
    }