CHECKPOINTS = [
    {
        "topic": "Introduction to Machine Learning",
        "objectives": [
            "Understand what Machine Learning is",
            "Differentiate ML from traditional programming"
        ]
    },
    {
        "topic": "Supervised vs Unsupervised Learning",
        "objectives": [
            "Understand supervised learning",
            "Understand unsupervised learning",
            "Compare supervised and unsupervised learning"
        ]
    },
    {
        "topic": "Overfitting and Underfitting",
        "objectives": [
            "Understand overfitting",
            "Understand underfitting",
            "Know how to reduce overfitting"
        ]
    }
]

def define_checkpoint(state):
    idx = state["current_checkpoint"]

    # 🛑 Stop condition
    if idx >= len(CHECKPOINTS):
        state["learning_complete"] = True
        return state

    checkpoint = CHECKPOINTS[idx]

    state["topic"] = checkpoint["topic"]
    state["objectives"] = checkpoint["objectives"]
    state["retry_count"] = 0
    state["weak_objectives"] = []

    return state
