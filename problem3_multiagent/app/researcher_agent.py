import logging
import os
from typing import List, Dict, Any

from langchain_core.language_models import BaseLanguageModel
from langchain_google_genai import ChatGoogleGenerativeAI

from app.cache_manager import get_cache

logger = logging.getLogger(__name__)


class ResearcherAgent:
    """Agent for extracting key entities and facts from raw data."""

    def __init__(self, model: BaseLanguageModel = None):
        if model is None:
            api_key = os.getenv("GEMINI_API_KEY")
            model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
            model = ChatGoogleGenerativeAI(api_key=api_key, model=model_name)
        
        self.model = model
        self.cache = get_cache()

    def extract_facts(self, content: str) -> Dict[str, Any]:
        """Extract key facts and entities from content."""
        cache_key = f"researcher_facts_{hash(content) % 10000}"
        
        # Check cache
        cached_result = self.cache.get(cache_key)
        if cached_result:
            logger.info("Using cached facts for content hash")
            return cached_result
        
        prompt = f"""You are a research analyst. Extract key facts and entities from the following content.

Content:
{content}

Provide a JSON response with:
{{
    "key_facts": [list of important facts],
    "entities": [list of named entities like people, places, organizations],
    "dates": [any important dates mentioned],
    "numbers": [any significant numbers or statistics],
    "summary": "brief summary of main points"
}}

Respond ONLY with valid JSON, no additional text."""
        
        try:
            logger.info("Extracting facts using researcher agent")
            response = self.model.invoke(prompt)
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Parse JSON response
            import json
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    result = json.loads(json_match.group())
                else:
                    result = {
                        "key_facts": [response_text],
                        "entities": [],
                        "dates": [],
                        "numbers": [],
                        "summary": response_text
                    }
            
            # Cache the result
            self.cache.set(cache_key, result)
            return result
        except Exception as e:
            logger.error("Error extracting facts: %s", e)
            return {
                "key_facts": [],
                "entities": [],
                "dates": [],
                "numbers": [],
                "summary": f"Error: {str(e)}"
            }

    def analyze_chunk(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single data chunk for facts."""
        content = chunk.get("content", "")
        chunk_id = chunk.get("chunk_id", "unknown")
        
        facts = self.extract_facts(content)
        
        return {
            "chunk_id": chunk_id,
            "source": chunk.get("source", "unknown"),
            "extracted_facts": facts,
            "confidence": "medium"
        }
