import os
import logging
import sys

# Add the parent directory to sys.path to allow imports from app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Any, Dict, List

from dotenv import load_dotenv
import google.generativeai as genai
from app.rag_pipeline import retrieve_documents

logger = logging.getLogger(__name__)

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-pro")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY must be set in .env")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL_NAME)


def generate_answer(prompt: str) -> str:
    logger.info("Generating answer using Gemini model")
    response = model.generate_content(prompt)
    answer = response.text.strip()
    logger.info("Generated answer with length: %d characters", len(answer))
    return answer


def build_prompt(query: str, context: str) -> str:
    return f"""
Context:
{context}

Question:
{query}

Answer:
"""


def evaluate_response(
    query: str, retrieved_docs: List[Any], answer: str
) -> Dict[str, float]:
    logger.info("Evaluating response for query: '%s'", query)
    context_relevance = round(min(len(retrieved_docs) / 3, 1.0), 2)
    faithfulness = round(
        0.9 if any(doc.page_content[:50] in answer for doc in retrieved_docs) else 0.5,
        2,
    )
    answer_relevance = round(
        0.9 if query.lower().split()[0] in answer.lower() else 0.6, 2
    )
    scores = {
        "context_relevance": context_relevance,
        "faithfulness": faithfulness,
        "answer_relevance": answer_relevance,
    }
    logger.info("Evaluation scores: %s", scores)
    return scores


if __name__ == "__main__":
    query = input("Enter your question: ")
    docs = retrieve_documents(query)
    context = "\n".join(doc.page_content for doc in docs)
    answer = generate_answer(build_prompt(query, context))
    scores = evaluate_response(query, docs, answer)
    print("\nGenerated Answer:\n", answer)
    print("\nEvaluation Scores:\n", scores)
