from typing import TypedDict, List

class LearningState(TypedDict):
    topic: str
    objectives: List[str]
    teaching_context: str   # ✅ REQUIRED
    mcqs: list
    user_answers: list
    score: float
    retry_count: int
    max_retries: int
