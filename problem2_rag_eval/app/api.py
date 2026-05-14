import asyncio
import logging
import sys
import os

# Add the parent directory to sys.path to allow imports from app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import Dict

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.log_config import configure_global_logger
from app.self_corrector import self_correct

# Configure logging to console and shared file
configure_global_logger()

logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Evaluation API")


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    query: str
    final_answer: str
    scores: Dict[str, float]


@app.get("/")
async def health_check() -> Dict[str, str]:
    logger.info("Health check requested")
    return {"status": "ok", "message": "RAG API is ready"}


@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest) -> QueryResponse:
    if not request.query.strip():
        logger.warning("Empty query received")
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    logger.info("Processing question: '%s'", request.query.strip())
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, self_correct, request.query.strip())
    logger.info("Question processed successfully")
    return {
        "query": request.query.strip(),
        "final_answer": result["final_answer"],
        "scores": result["final_scores"],
    }
