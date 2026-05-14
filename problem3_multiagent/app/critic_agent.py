import logging
import os
from typing import List, Dict, Any, Tuple

from langchain_core.language_models import BaseLanguageModel
from langchain_google_genai import ChatGoogleGenerativeAI

from app.cache_manager import get_cache

logger = logging.getLogger(__name__)


class CriticAgent:
    """Agent for verifying facts against original sources."""

    def __init__(self, model: BaseLanguageModel = None):
        if model is None:
            api_key = os.getenv("GEMINI_API_KEY")
            model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
            model = ChatGoogleGenerativeAI(api_key=api_key, model=model_name)
        
        self.model = model
        self.cache = get_cache()

    def verify_facts(
        self,
        facts: List[str],
        source_content: str
    ) -> List[Dict[str, Any]]:
        """Verify a list of facts against source content."""
        cache_key = f"critic_verify_{hash(str(facts) + source_content) % 10000}"
        
        cached_result = self.cache.get(cache_key)
        if cached_result:
            logger.info("Using cached verification results")
            return cached_result
        
        facts_str = "\n".join([f"- {fact}" for fact in facts])
        
        prompt = f"""You are a fact-checking expert. Verify the following facts against the provided source content.

Facts to verify:
{facts_str}

Source content:
{source_content}

For each fact, respond with a JSON array:
[
    {{
        "fact": "the original fact",
        "status": "verified|contradicted|unverified",
        "explanation": "brief explanation",
        "evidence": "relevant excerpt from source if verified"
    }}
]

Respond ONLY with valid JSON array, no additional text."""
        
        try:
            logger.info("Verifying %d facts using critic agent", len(facts))
            response = self.model.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            import json
            import re
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = [{"fact": f, "status": "unverified", "explanation": "Parse error"} for f in facts]
            
            self.cache.set(cache_key, result)
            return result
        except Exception as e:
            logger.error("Error verifying facts: %s", e)
            return [{"fact": f, "status": "error", "explanation": str(e)} for f in facts]

    def compare_across_sources(
        self,
        fact: str,
        source_chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare a fact across multiple source chunks."""
        result = {
            "fact": fact,
            "consistency": "consistent",
            "sources_checked": len(source_chunks),
            "verifications": []
        }
        
        for chunk in source_chunks:
            content = chunk.get("content", "")
            source = chunk.get("source", "unknown")
            chunk_id = chunk.get("chunk_id", "unknown")
            
            verification = self.verify_facts([fact], content)
            
            if verification:
                status = verification[0].get("status", "unverified")
                result["verifications"].append({
                    "source": source,
                    "chunk_id": chunk_id,
                    "status": status,
                    "explanation": verification[0].get("explanation", "")
                })
        
        # Determine overall consistency
        statuses = [v.get("status") for v in result["verifications"]]
        if all(s == "verified" for s in statuses if s):
            result["consistency"] = "consistent"
        elif any(s == "contradicted" for s in statuses):
            result["consistency"] = "contradicted"
        else:
            result["consistency"] = "partially_verified"
        
        return result
