import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.data_ingestion import DataIngestionService
from app.researcher_agent import ResearcherAgent
from app.critic_agent import CriticAgent
from app.synthesizer_agent import SynthesizerAgent
from app.cache_manager import get_cache

logger = logging.getLogger(__name__)


class MultiAgentOrchestrator:
    """Orchestrates the multi-agent workflow for content synthesis and fact-checking."""

    def __init__(self):
        """Initialize all agents and services."""
        logger.info("Initializing Multi-Agent Orchestrator")
        
        self.ingestor = DataIngestionService()
        self.researcher = ResearcherAgent()
        self.critic = CriticAgent()
        self.synthesizer = SynthesizerAgent()
        self.cache = get_cache()

    async def process_sources(
        self,
        sources: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process and ingest multiple sources (PDFs, web links, JSON logs).
        
        sources: List of dicts with 'type' (pdf|web|json|text), 'path'/'url' keys
        Returns: List of ingested chunks with metadata
        """
        all_chunks = []
        
        for source in sources:
            source_type = source.get("type", "").lower()
            location = source.get("path") or source.get("url")
            
            if not location:
                logger.warning("Source missing path/url: %s", source)
                continue
            
            logger.info("Processing source type=%s location=%s", source_type, location)
            
            if source_type == "pdf":
                chunks = self.ingestor.ingest_pdf(location)
            elif source_type == "web":
                chunks = self.ingestor.ingest_web_link(location)
            elif source_type == "json":
                chunks = self.ingestor.ingest_json_logs(location)
            elif source_type == "text":
                chunks = self.ingestor.ingest_text_file(location)
            else:
                logger.warning("Unknown source type: %s", source_type)
                continue
            
            all_chunks.extend(chunks)
        
        logger.info("Ingested %d total chunks from %d sources", len(all_chunks), len(sources))
        return all_chunks

    async def deduplicate_content(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Deduplicate content (simplified version without embeddings)."""
        logger.info("Deduplication skipped for simplicity")
        return chunks

    async def extract_facts(
        self,
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract facts from each chunk using the researcher agent."""
        logger.info("Extracting facts from %d chunks", len(chunks))
        
        extracted = []
        for chunk in chunks:
            analysis = self.researcher.analyze_chunk(chunk)
            extracted.append(analysis)
        
        logger.info("Extracted facts from %d chunks", len(extracted))
        return extracted

    async def verify_facts(
        self,
        extracted_facts: List[Dict[str, Any]],
        chunks: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Verify extracted facts against source content using the critic agent."""
        logger.info("Verifying facts across sources")
        
        verified_facts = []
        
        # Group chunks by source for cross-source verification
        chunks_by_source = {}
        for chunk in chunks:
            source = chunk.get("source", "unknown")
            if source not in chunks_by_source:
                chunks_by_source[source] = []
            chunks_by_source[source].append(chunk)
        
        for fact_analysis in extracted_facts:
            chunk_id = fact_analysis.get("chunk_id")
            extracted = fact_analysis.get("extracted_facts", {})
            key_facts = extracted.get("key_facts", [])
            
            # Verify against all sources
            for fact in key_facts:
                cross_verify = self.critic.compare_across_sources(fact, chunks)
                
                verified_facts.append({
                    "fact": fact,
                    "chunk_id": chunk_id,
                    "source": fact_analysis.get("source"),
                    "consistency": cross_verify.get("consistency"),
                    "verifications": cross_verify.get("verifications", []),
                    "status": "verified" if cross_verify.get("consistency") == "consistent" else "unverified"
                })
        
        logger.info("Verified %d facts", len(verified_facts))
        return verified_facts

    async def synthesize_report(
        self,
        verified_facts: List[Dict[str, Any]],
        topic: str = "Technical Report"
    ) -> Dict[str, Any]:
        """Generate final markdown report with source citations."""
        logger.info("Synthesizing report on topic: %s", topic)
        
        # Generate base report
        report = self.synthesizer.synthesize_report(verified_facts, topic)
        
        # Add table of contents
        report_with_toc = self.synthesizer.generate_toc(report)
        
        # Add source citations
        final_report = self.synthesizer.add_source_citations(report_with_toc, verified_facts)
        
        result = {
            "topic": topic,
            "report": final_report,
            "facts_count": len(verified_facts),
            "verified_count": len([f for f in verified_facts if f.get("status") == "verified"]),
            "generated_at": datetime.now().isoformat()
        }
        
        logger.info("Report synthesis complete: %d facts included", len(verified_facts))
        return result

    async def run_pipeline(
        self,
        sources: List[Dict[str, Any]],
        topic: str = "Technical Report"
    ) -> Dict[str, Any]:
        """Run the complete multi-agent pipeline."""
        logger.info("Starting multi-agent pipeline for topic: %s", topic)
        
        # Step 1: Ingest data
        chunks = await self.process_sources(sources)
        if not chunks:
            logger.error("No chunks ingested from sources")
            return {"error": "No data ingested"}
        
        # Step 2: Deduplicate content
        deduplicated_chunks = await self.deduplicate_content(chunks)
        
        # Step 3: Extract facts
        extracted_facts = await self.extract_facts(deduplicated_chunks)
        
        # Step 4: Verify facts
        verified_facts = await self.verify_facts(extracted_facts, deduplicated_chunks)
        
        # Step 5: Synthesize report
        final_output = await self.synthesize_report(verified_facts, topic)
        
        # Add metadata
        final_output["pipeline_stats"] = {
            "input_chunks": len(chunks),
            "deduplicated_chunks": len(deduplicated_chunks),
            "facts_extracted": len(extracted_facts),
            "facts_verified": len(verified_facts)
        }
        
        logger.info("Pipeline complete. Generated report with %d verified facts", len(verified_facts))
        return final_output
