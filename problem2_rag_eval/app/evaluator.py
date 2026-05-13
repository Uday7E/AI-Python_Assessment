from transformers import pipeline
from rag_pipeline import retrieve_documents

generator = pipeline(
    "text-generation",
    model="distilgpt2"
)


def generate_answer(query, context):
    prompt = f"""
Context:
{context}

Question:
{query}

Answer:
"""

    response = generator(
        prompt,
        max_length=200,
        num_return_sequences=1
    )

    answer = response[0]["generated_text"]

    return answer


def evaluate_response(query, retrieved_docs, answer):

    context_relevance = round(min(len(retrieved_docs) / 3, 1.0), 2)

    faithfulness = round(
        0.9 if any(
            doc.page_content[:50] in answer
            for doc in retrieved_docs
        ) else 0.5,
        2
    )

    answer_relevance = round(
        0.9 if query.lower().split()[0] in answer.lower() else 0.6,
        2
    )

    return {
        "context_relevance": context_relevance,
        "faithfulness": faithfulness,
        "answer_relevance": answer_relevance
    }


if __name__ == "__main__":

    query = input("Enter your question: ")

    docs = retrieve_documents(query)

    context = "\n".join([doc.page_content for doc in docs])

    answer = generate_answer(query, context)

    scores = evaluate_response(query, docs, answer)

    print("\nGenerated Answer:\n")
    print(answer)

    print("\nEvaluation Scores:\n")
    print(scores)