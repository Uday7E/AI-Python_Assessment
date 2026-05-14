import logging
import os
from typing import List, Dict, Any

from langchain_core.language_model import BaseLanguageModel
from langchain_google_genai import ChatGoogleGenerativeAI

from app.cache_manager import get_cache

logger = logging.getLogger(__name__)


class SynthesizerAgent:
    """Agent for compiling final verified facts into a structured markdown report."""

    def __init__(self, model: BaseLanguageModel = None):
        if model is None:
            api_key = os.getenv("GEMINI_API_KEY")
            model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
            model = ChatGoogleGenerativeAI(api_key=api_key, model=model_name)
        
        self.model = model
        self.cache = get_cache()

    def synthesize_report(
        self,
        verified_facts: List[Dict[str, Any]],
        topic: str = "Technical Report"
    ) -> str:
        """Compile verified facts into a structured markdown report."""
        cache_key = f"synthesizer_report_{hash(topic + str(len(verified_facts))) % 10000}"
        
        cached_result = self.cache.get(cache_key)
        if cached_result:
            logger.info("Using cached synthesized report")
            return cached_result
        
        # Format verified facts for the prompt
        facts_text = ""
        for fact_item in verified_facts:
            if isinstance(fact_item, dict):
                fact = fact_item.get("fact", "")
                status = fact_item.get("status", "unverified")
                sources = fact_item.get("sources", [])
                facts_text += f"\n- {fact} (Status: {status}, Sources: {', '.join(sources)})"
            else:
                facts_text += f"\n- {str(fact_item)}"
        
        prompt = f"""You are a technical report writer. Create a well-structured markdown report from the following verified facts.

Topic: {topic}

Verified Facts:
{facts_text}

Create a markdown report with:
1. Executive Summary
2. Key Findings (organized by category)
3. Detailed Analysis
4. Conclusions
5. Source References

Format as proper markdown with headers, bullet points, and clear structure."""
        
        try:
            logger.info("Synthesizing report on topic: %s", topic)
            response = self.model.invoke(prompt)
            report = response.content if hasattr(response, 'content') else str(response)
            
            self.cache.set(cache_key, report)
            return report
        except Exception as e:
            logger.error("Error synthesizing report: %s", e)
            return f"# Error Generating Report\n\nAn error occurred during synthesis: {str(e)}"

    def add_source_citations(
        self,
        report: str,
        cited_facts: List[Dict[str, Any]]
    ) -> str:
        """Enhance report with source citations."""
        citation_map = {}
        
        for fact_item in cited_facts:
            fact = fact_item.get("fact", "")
            sources = fact_item.get("sources", [])
            chunk_ids = fact_item.get("chunk_ids", [])
            
            if sources and chunk_ids:
                citation_map[fact] = {
                    "sources": sources,
                    "chunk_ids": chunk_ids
                }
        
        # Build citations section
        citations_section = "\n\n## Source Citations\n\n"
        
        for idx, (fact, citation_info) in enumerate(citation_map.items(), 1):
            sources = citation_info.get("sources", [])
            chunk_ids = citation_info.get("chunk_ids", [])
            citations_section += f"\n[{idx}] {fact}\n"
            for source, chunk_id in zip(sources, chunk_ids):
                citations_section += f"   - Source: {source} (Chunk ID: {chunk_id})\n"
        
        return report + citations_section

    def generate_toc(self, report: str) -> str:
        """Generate table of contents for the report."""
        import re
        
        headers = re.findall(r'^(#{1,6})\s+(.+)$', report, re.MULTILINE)
        
        if not headers:
            return report
        
        toc = "## Table of Contents\n\n"
        for level, title in headers:
            indent = "  " * (len(level) - 1)
            toc += f"{indent}- {title}\n"
        
        # Insert TOC after first header
        first_header_end = report.find('\n') + 1
        return report[:first_header_end] + toc + "\n" + report[first_header_end:]
