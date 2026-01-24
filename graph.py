from langgraph.graph import StateGraph, END
from state import LearningState

from nodes.explain_topic import explain_topic
from nodes.generate_questions import generate_questions
from nodes.evaluate_answers import evaluate_answers
from nodes.feynman_teach import feynman_teach


def decide_score(state):
    if state["score"] >= 70:
        return "pass"
    elif state["retry_count"] < state["max_retries"]:
        return "retry"
    else:
        return "stop"


def build_teach_graph():
    graph = StateGraph(LearningState)
    graph.add_node("explain_topic", explain_topic)
    graph.set_entry_point("explain_topic")
    graph.add_edge("explain_topic", END)
    return graph.compile()


def build_quiz_graph():
    graph = StateGraph(LearningState)

    graph.add_node("generate_questions", generate_questions)
    graph.add_node("evaluate_answers", evaluate_answers)
    graph.add_node("feynman_teach", feynman_teach)

    graph.set_entry_point("generate_questions")
    graph.add_edge("generate_questions", "evaluate_answers")

    graph.add_conditional_edges(
        "evaluate_answers",
        decide_score,
        {
            "pass": END,
            "retry": "feynman_teach",
            "stop": END,
        },
    )

    graph.add_edge("feynman_teach", "generate_questions")

    return graph.compile()
