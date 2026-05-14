import os
import uuid
import logging
import sys

# Add the parent directory to sys.path to allow imports from app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Any, Dict

from app.evaluator import generate_answer, evaluate_response, build_prompt
from app.rag_pipeline import retrieve_documents, save_result

logger = logging.getLogger(__name__)

FAITHFULNESS_THRESHOLD = 0.7
LLM_MODEL = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-pro")


def self_correct(query: str) -> Dict[str, Any]:
    logger.info("Starting self-correction process for query: '%s'", query)
    docs = retrieve_documents(query)
    context = "\n".join(doc.page_content for doc in docs)
    prompt = build_prompt(query, context)
    answer = generate_answer(prompt)
    scores = evaluate_response(query, docs, answer)
    self_correction_triggered = False

    if scores["faithfulness"] < FAITHFULNESS_THRESHOLD:
        logger.info("Faithfulness score %.2f below threshold %.2f, triggering self-correction", scores["faithfulness"], FAITHFULNESS_THRESHOLD)
        self_correction_triggered = True
        strict_prompt = f"""
Answer ONLY using the provided context.
Do not hallucinate.

Context:
{context}

Question:
{query}

Answer:
"""
        answer = generate_answer(strict_prompt)
        scores = evaluate_response(query, docs, answer)
        logger.info("Self-correction completed, new faithfulness score: %.2f", scores["faithfulness"])

    record = {
        "run_id": str(uuid.uuid4()),
        "user_query": query,
        "retrieved_context": context,
        "generated_answer": answer,
        "final_answer": answer,
        "context_relevance_score": scores["context_relevance"],
        "faithfulness_score": scores["faithfulness"],
        "answer_relevance_score": scores["answer_relevance"],
        "hallucination_detected": scores["faithfulness"] < FAITHFULNESS_THRESHOLD,
        "self_correction_triggered": self_correction_triggered,
        "correction_attempts": 1 if self_correction_triggered else 0,
        "evaluation_summary": "auto-evaluated",
        "llm_model": LLM_MODEL,
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
        "vector_store": "Chroma",
        "chunking_strategy": "recursive-character-splitter",
    }
    save_result(record)
    logger.info("Self-correction process completed, result saved")
    return {"final_answer": answer, "final_scores": scores}


if __name__ == "__main__":
    query = input("Ask a question: ")
    result = self_correct(query)
    print("\nFinal Answer:\n", result["final_answer"])
    print("\nFinal Evaluation Scores:\n", result["final_scores"])
