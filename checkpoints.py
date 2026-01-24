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
