import asyncio
import logging
from typing import List, Dict, Any
import os

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from app.log_config import configure_global_logger
from app.orchestrator import MultiAgentOrchestrator

load_dotenv()
configure_global_logger()

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Multi-Agent Content Synthesizer & Fact-Checker",
    description="End-to-end multi-agent orchestration for content synthesis and fact verification"
)

# Global orchestrator instance
orchestrator = MultiAgentOrchestrator()


class Source(BaseModel):
    """Source document model."""
    type: str  # pdf, web, json, text
    path: str = None  # For local files
    url: str = None   # For web links


class ReportRequest(BaseModel):
    """Request to generate a report."""
    sources: List[Source]
    topic: str = "Technical Report"


class ReportResponse(BaseModel):
    """Response with generated report."""
    topic: str
    report: str
    facts_count: int
    verified_count: int
    pipeline_stats: Dict[str, Any]
    generated_at: str


@app.get("/health")
def health_check():
    """Health check endpoint."""
    logger.info("Health check requested")
    return {"status": "healthy", "service": "multi-agent-synthesizer"}


@app.post("/generate-report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """Generate a comprehensive report from multiple sources."""
    try:
        if not request.sources:
            logger.warning("Empty sources list received")
            raise HTTPException(status_code=400, detail="At least one source is required")
        
        # Convert source objects to dicts
        sources = [
            {
                "type": s.type,
                "path": s.path,
                "url": s.url
            }
            for s in request.sources
        ]
        
        logger.info("Generating report for topic: '%s' with %d sources", request.topic, len(sources))
        
        # Run orchestrator pipeline
        result = await orchestrator.run_pipeline(sources, request.topic)
        
        if "error" in result:
            logger.error("Pipeline error: %s", result["error"])
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error generating report: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/cache/clear")
def clear_cache():
    """Clear the query cache."""
    try:
        cache = orchestrator.cache
        cache.clear()
        logger.info("Cache cleared")
        return {"status": "cache cleared"}
    except Exception as e:
        logger.error("Error clearing cache: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
