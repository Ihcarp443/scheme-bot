from services.feedback_improver import improve_answer


def feedback_improve_node(state):

    improved_answer = improve_answer(
        question=state["question"],
        answer=state["original_answer"],
        reason=state.get("feedback_reason"),
        comment=state.get("feedback_comment")
    )

    return {
        "answer_en": improved_answer,
        "final_answer": improved_answer,
        "feedback_mode": False
    }