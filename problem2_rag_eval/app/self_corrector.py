from evaluator import (
    generate_answer,
    evaluate_response
)

from rag_pipeline import retrieve_documents


FAITHFULNESS_THRESHOLD = 0.7


def self_correct(query):

    docs = retrieve_documents(query)

    context = "\n".join(
        [doc.page_content for doc in docs]
    )

    answer = generate_answer(query, context)

    scores = evaluate_response(
        query,
        docs,
        answer
    )

    print("\nInitial Scores:\n")
    print(scores)

    if scores["faithfulness"] < FAITHFULNESS_THRESHOLD:

        print("\nLow faithfulness detected.")
        print("Regenerating answer...\n")

        improved_prompt = f"""
Answer ONLY using the provided context.
Do not hallucinate.

Context:
{context}

Question:
{query}

Answer:
"""

        corrected_answer = generate_answer(
            query,
            improved_prompt
        )

        corrected_scores = evaluate_response(
            query,
            docs,
            corrected_answer
        )

        return {
            "final_answer": corrected_answer,
            "final_scores": corrected_scores
        }

    return {
        "final_answer": answer,
        "final_scores": scores
    }


if __name__ == "__main__":

    query = input("Ask a question: ")

    result = self_correct(query)

    print("\nFinal Answer:\n")
    print(result["final_answer"])

    print("\nFinal Evaluation Scores:\n")
    print(result["final_scores"])