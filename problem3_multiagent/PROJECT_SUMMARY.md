# Project Summary: Multi-Agent Content Synthesizer & Fact-Checker

## Overview

A complete **end-to-end multi-agent orchestration system** built to solve the problem of synthesizing high-quality technical reports from multiple disparate sources with automated fact verification and source citation tracking.

**Problem Statement 3**: Generate technical reports from PDFs, web links, and JSON logs while verifying facts across sources to eliminate hallucinations and contradictions.

## What Was Built

### Core Architecture

```
Data Sources (PDF/Web/JSON/Text)
         ↓
   Data Ingestion (multi-format support)
         ↓
   Semantic Deduplication (cosine similarity >= 0.85)
         ↓
   ┌─────────────────────────────────┐
   │   Researcher Agent              │  Extract facts, entities, dates, numbers
   │   Critic Agent                  │  Verify facts across sources
   │   Synthesizer Agent             │  Compile final report with citations
   └─────────────────────────────────┘
         ↓
   Final Markdown Report with Source Citations & Chunk IDs
```

### Key Components

| Component | File | Purpose |
|-----------|------|---------|
| **Data Ingestion** | `data_ingestion.py` | Load PDFs, web content, JSON logs, text files |
| **Embeddings** | `embedding_service.py` | Semantic embeddings + duplicate detection |
| **Researcher Agent** | `researcher_agent.py` | Extract facts using Gemini API |
| **Critic Agent** | `critic_agent.py` | Verify facts across sources |
| **Synthesizer Agent** | `synthesizer_agent.py` | Compile reports with citations |
| **Orchestrator** | `orchestrator.py` | Coordinate multi-agent pipeline |
| **Caching Layer** | `cache_manager.py` | DiskCache to avoid redundant API calls |
| **FastAPI Backend** | `api.py` | REST API with /generate-report endpoint |
| **Streamlit Frontend** | `streamlit_app.py` | Interactive web UI |
| **Logging** | `log_config.py` | Shared logging to file + console |

### Complete Feature Set

✅ **Multi-Source Data Ingestion**
- PDF documents (via PDFPlumber)
- Web links (HTTP requests)
- JSON logs (structured data)
- Plain text files

✅ **Semantic Deduplication**
- Sentence Transformers embeddings
- Cosine similarity detection
- Configurable threshold (0.85 default)
- Merges duplicates while tracking all sources

✅ **Multi-Agent Orchestration**
- Researcher: Extracts facts, entities, dates, numbers
- Critic: Verifies facts across all sources
- Synthesizer: Compiles final markdown report
- Async/await for concurrent processing

✅ **Source Citation Engine**
- Each fact tracked to original chunk
- Chunk IDs preserved throughout pipeline
- Final report includes source references
- Cross-source verification metadata

✅ **Intelligent Caching**
- DiskCache for persistent storage
- Falls back to in-memory dict if needed
- Avoids redundant LLM API calls
- Cache keys based on content hash

✅ **Comprehensive Logging**
- All activity logged to `logs/multiagent.log`
- Console + file output
- Timestamps and module names
- Pipeline statistics tracking

✅ **REST API & Web UI**
- FastAPI backend with FastAPI docs
- Streamlit interactive interface
- Download report as markdown
- View statistics and metadata

✅ **Docker Support**
- Multi-container setup (API + Frontend)
- docker-compose.yml for easy deployment
- Shared volumes for data/logs/cache

## How It Differs From Problem 2 (RAG Evaluation)

### Problem 2: RAG Evaluation Tool
- **Focus**: Single LLM query → retrieve context → evaluate response quality
- **Agents**: One implicit "evaluator" component
- **Output**: Answer with evaluation metrics (faithfulness, relevance)
- **Sources**: Internal documents only
- **Citation**: Basic reference to retrieved chunks

### Problem 3: Multi-Agent Synthesizer (NEW)
- **Focus**: Multiple agents with distinct roles collaborating
- **Agents**: Researcher (extract) + Critic (verify) + Synthesizer (compile)
- **Output**: Structured markdown report with fact verification status
- **Sources**: PDFs, web links, JSON logs, text files
- **Citation**: Precise chunk IDs with cross-source verification
- **Innovation**: Semantic deduplication + fact contradiction detection

## Project Structure

```
problem3_multiagent/
├── app/
│   ├── __init__.py
│   ├── log_config.py              ← Shared logging
│   ├── cache_manager.py           ← DiskCache layer
│   ├── embedding_service.py       ← Semantic embeddings
│   ├── data_ingestion.py          ← Multi-source loading
│   ├── researcher_agent.py        ← Fact extraction
│   ├── critic_agent.py            ← Fact verification
│   ├── synthesizer_agent.py       ← Report compilation
│   ├── orchestrator.py            ← Pipeline coordination
│   ├── api.py                     ← FastAPI backend
│   └── streamlit_app.py           ← Web UI
├── data/                          ← Sample inputs
│   ├── sample_document.txt
│   └── sample_events.json
├── logs/                          ← Runtime logs
├── cache/                         ← Cached results
├── requirements.txt               ← Dependencies
├── .env.example                   ← Config template
├── .gitignore
├── docker-compose.yml
├── Dockerfile (API)
├── Dockerfile.streamlit
├── README.md                      ← Full documentation
├── QUICKSTART.md                  ← 5-minute setup
├── CONFIG.md                      ← Configuration guide
└── PROJECT_SUMMARY.md             ← This file
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Framework** | FastAPI, Streamlit, LangChain |
| **LLM** | Google Gemini 2.5 Flash |
| **Embeddings** | Sentence Transformers (all-MiniLM-L6-v2) |
| **Data Processing** | PDFPlumber, Requests, Python |
| **Caching** | DiskCache (+ fallback) |
| **Async** | asyncio |
| **Containerization** | Docker, Docker Compose |
| **Language** | Python 3.11+ |

## Quick Start (< 5 minutes)

```bash
# 1. Setup
cd problem3_multiagent
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env: add GEMINI_API_KEY

# 3. Run
# Terminal 1:
uvicorn app.api:app --reload

# Terminal 2:
streamlit run app/streamlit_app.py

# 4. Use
# Open http://localhost:8501
# Add a source (try ./data/sample_document.txt)
# Generate report!
```

## Key Innovation: Fact Verification

Unlike traditional LLM synthesis, this system:

1. **Extracts facts from each source** independently
2. **Verifies each fact against other sources** for contradictions
3. **Tracks verification status**: verified | contradicted | unverified
4. **Preserves source citations** with precise chunk IDs
5. **Detects inconsistencies** across sources automatically

Example output snippet:
```
[1] Cloud security requires zero-trust architecture
   - Source: security_guide.pdf (Chunk ID: a1b2c3d4)
   - Status: verified by 3 sources
   
[2] All data must be encrypted at rest
   - Source: best_practices.json (Chunk ID: e5f6g7h8)
   - Status: verified by 2 sources
   
[3] Legacy systems don't need updates
   - Source: outdated_report.json (Chunk ID: i9j0k1l2)
   - Status: CONTRADICTED by security_guide.pdf
```

## Performance Characteristics

- **Input**: 1-10 documents (PDFs, web pages, JSON)
- **Processing Time**: 1-5 minutes (depends on size)
- **Caching**: Subsequent identical queries << 1 second
- **Output**: Markdown report (2000-10000 words)
- **API Rate**: ~60 requests/minute (free tier)

## Advanced Features

### 1. Semantic Deduplication
Automatically merges duplicate information:
- Threshold: 0.85 cosine similarity
- Preserves all source references
- Reduces processing overhead

### 2. Multi-Format Support
- PDFs (via PDFPlumber)
- Web pages (HTTP requests)
- JSON/JSONL files
- Plain text

### 3. Intelligent Caching
- Content-based cache keys
- Avoids redundant API calls
- Persistent storage (DiskCache)
- In-memory fallback

### 4. Structured Output
- Markdown format
- Executive summary
- Table of contents
- Section organization
- Source citations

### 5. Cross-Source Verification
- Compares facts across all sources
- Identifies contradictions
- Tracks verification confidence
- Reports consistency status

## Usage Scenarios

### Scenario 1: Technical Documentation
**Input**: Various product docs, GitHub READMEs, forum posts
**Output**: Unified, fact-checked technical specification

### Scenario 2: Competitive Analysis
**Input**: Competitor reports, news articles, financial statements
**Output**: Verified competitive analysis with source attribution

### Scenario 3: Regulatory Compliance
**Input**: Audit logs, policy documents, compliance reports
**Output**: Consolidated compliance report with verification

### Scenario 4: Literature Review
**Input**: Academic papers, articles, preprints
**Output**: Synthesized review with fact-checked summaries

## Deployment Options

### Option 1: Local Development
```bash
uvicorn app.api:app --reload
streamlit run app/streamlit_app.py
```

### Option 2: Docker
```bash
docker-compose up --build
```

### Option 3: Cloud (AWS/GCP/Azure)
- Push Docker images to registry
- Deploy on Kubernetes or container service
- Use cloud-managed LLM endpoints

## Next Steps / Future Enhancements

- [ ] Redis support for distributed caching
- [ ] Fact confidence scoring system
- [ ] Multi-language support
- [ ] HTML/PDF export options
- [ ] Real-time streaming report generation
- [ ] Debate mode (agents arguing different positions)
- [ ] Integration with multiple LLM providers
- [ ] Web UI improvements (drag-drop files, preview)
- [ ] GraphQL API in addition to REST
- [ ] Analytics dashboard

## Files Reference

| File | Lines | Purpose |
|------|-------|---------|
| orchestrator.py | ~250 | Main pipeline coordinator |
| data_ingestion.py | ~200 | Multi-source data loading |
| embedding_service.py | ~180 | Semantic embeddings + deduplication |
| researcher_agent.py | ~80 | Fact extraction |
| critic_agent.py | ~110 | Fact verification |
| synthesizer_agent.py | ~100 | Report generation |
| api.py | ~100 | FastAPI backend |
| streamlit_app.py | ~150 | Web UI |
| cache_manager.py | ~140 | Caching layer |
| Total Code | ~1200 | ~1200 lines of production code |

## Testing the System

### Test 1: Simple Text File
```
1. Add source: ./data/sample_document.txt
2. Topic: "Multi-Agent Systems"
3. Generate → Should extract 5-8 facts
```

### Test 2: Multiple Sources
```
1. Add source 1: ./data/sample_document.txt
2. Add source 2: ./data/sample_events.json
3. Topic: "System Analysis"
4. Generate → Should find 2-3 duplicate concepts
```

### Test 3: Web Source
```
1. Add source: https://en.wikipedia.org/wiki/Artificial_intelligence
2. Topic: "AI History"
3. Generate → Should extract facts from web content
```

## Common Commands

```bash
# View logs
tail -f logs/multiagent.log

# Clear cache
rm -rf cache/*

# Test API
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs

# Check environment
python -c "import app; print('Setup OK')"
```

## Support & Debugging

**Issue**: API returns error
→ Check `logs/multiagent.log` for details
→ Verify `.env` has valid `GEMINI_API_KEY`

**Issue**: Slow processing
→ Check cache is working (should see "Cache HIT" in logs)
→ Reduce `CHUNK_SIZE` in `data_ingestion.py`

**Issue**: Out of memory
→ Process fewer sources at once
→ Clear cache: `rm -rf cache/`

**Issue**: Inaccurate results
→ Adjust `SIMILARITY_THRESHOLD` in `embedding_service.py`
→ Use larger embedding model

---

## Comparison: Problem 2 vs Problem 3

| Aspect | Problem 2 | Problem 3 |
|--------|-----------|----------|
| **Task** | Evaluate single LLM response | Synthesize multi-source report |
| **Agent Count** | 1 implicit | 3 explicit (Researcher, Critic, Synthesizer) |
| **Source Types** | Internal documents only | PDF, Web, JSON, Text |
| **Key Innovation** | Self-correction loop | Fact verification across sources |
| **Output Type** | Answer + evaluation scores | Structured markdown report |
| **Citation Tracking** | Basic chunk references | Precise chunk IDs + source info |
| **Cache Usage** | Query caching | Query + embedding + verification caching |
| **Complexity** | Medium | High |
| **Lines of Code** | ~800 | ~1200 |

---

**Built with ❤️ using LangChain, Google Gemini, FastAPI, and Streamlit**

See `README.md` for full documentation, `QUICKSTART.md` for setup, and `CONFIG.md` for configuration options.
