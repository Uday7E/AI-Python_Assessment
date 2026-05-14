# Multi-Agent Content Synthesizer & Fact-Checker

## Overview

This project implements an advanced **multi-agent orchestration system** that synthesizes comprehensive technical reports from disparate data sources (PDFs, web links, JSON logs) while verifying facts across sources to eliminate hallucinations and contradictions.

The system uses AI agents with distinct roles that collaborate to produce high-quality, fact-checked reports with full source citation tracking.

### Key Features
✅ **Multi-Source Integration** - PDFs, web links, JSON logs, text files  
✅ **Semantic Deduplication** - Eliminate duplicate content using embeddings  
✅ **Multi-Agent Orchestration** - Researcher, Critic, Synthesizer agents  
✅ **Fact Verification** - Cross-source verification with contradiction detection  
✅ **Source Citation** - Every fact traced back to original chunk  
✅ **Intelligent Caching** - Avoid redundant LLM API calls  
✅ **REST API** - FastAPI with interactive docs  
✅ **Web UI** - Streamlit interface for easy interaction  
✅ **Docker Support** - Multi-container deployment ready  

---

## Problem Statement

**Use Case:** Your team needs to generate high-quality technical reports from multiple disparate sources with nuanced fact verification.

**Challenge:** A single LLM call often misses nuances or conflates facts from different sources.

**Solution:** Multi-agent orchestration with semantic reconciliation and source citation engine.

---

## Architecture

### End-to-End Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA INGESTION LAYER                         │
├─────────────────────────────────────────────────────────────────────┤
│  PDFs  │  Web Links  │  JSON Logs  │  Text Files                    │
└────────┬──────────────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    SEMANTIC DEDUPLICATION LAYER                      │
├─────────────────────────────────────────────────────────────────────┤
│ • Generate embeddings for all chunks                                 │
│ • Find semantically similar content (cosine similarity >= 0.85)      │
│ • Merge duplicates while tracking sources                            │
└────────┬──────────────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────────────────┐
│                      RESEARCHER AGENT LAYER                          │
├─────────────────────────────────────────────────────────────────────┤
│ Agent Role: Extract Facts & Entities                                │
│ • Identify key facts, entities, dates, numbers                      │
│ • Generate summaries per chunk                                      │
│ • Cache results to avoid redundant LLM calls                        │
└────────┬──────────────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────────────────┐
│                       CRITIC AGENT LAYER                             │
├─────────────────────────────────────────────────────────────────────┤
│ Agent Role: Verify Facts & Detect Contradictions                    │
│ • Cross-verify facts across all sources                             │
│ • Mark as: verified | contradicted | unverified                     │
│ • Track evidence and contradictions                                 │
│ • Cache verification results                                        │
└────────┬──────────────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────────────────┐
│                   SYNTHESIZER AGENT LAYER                            │
├─────────────────────────────────────────────────────────────────────┤
│ Agent Role: Compile Final Report                                    │
│ • Create structured markdown report                                 │
│ • Organize facts by category                                        │
│ • Add table of contents                                             │
│ • Embed source citations and chunk IDs                              │
└────────┬──────────────────────────────────────────────────────────────┘
         │
         ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    FINAL OUTPUT WITH CITATIONS                       │
├─────────────────────────────────────────────────────────────────────┤
│ • Markdown report with full formatting                              │
│ • Source citations with chunk IDs                                   │
│ • Verification status for each fact                                 │
│ • Pipeline statistics and metadata                                  │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Components

#### 1. **DataIngestionService** (`data_ingestion.py`)
- Loads PDFs using PDFPlumber
- Fetches web content via HTTP
- Parses JSON logs and text files
- Splits all content into semantic chunks
- Tracks source metadata and chunk IDs

#### 2. **EmbeddingService** (`embedding_service.py`)
- Generates embeddings using Sentence Transformers (all-MiniLM-L6-v2)
- Computes cosine similarity between vectors
- Identifies duplicate/near-duplicate content (threshold: 0.85)
- Merges duplicates while preserving source references

#### 3. **ResearcherAgent** (`researcher_agent.py`)
- Extracts key facts, entities, dates, numbers from chunks
- Generates summaries using Google Gemini
- Results cached to avoid redundant API calls
- Returns structured JSON with extracted information

#### 4. **CriticAgent** (`critic_agent.py`)
- Verifies facts against source content
- Marks facts as: `verified | contradicted | unverified`
- Performs cross-source verification
- Caches verification results

#### 5. **SynthesizerAgent** (`synthesizer_agent.py`)
- Compiles verified facts into structured markdown
- Adds table of contents
- Generates source citation section
- Returns final polished report

#### 6. **MultiAgentOrchestrator** (`orchestrator.py`)
- Coordinates the entire pipeline asynchronously
- Manages agent communication and data flow
- Tracks pipeline statistics
- Handles error recovery

#### 7. **CacheManager** (`cache_manager.py`)
- Uses DiskCache for persistent caching (or in-memory fallback)
- Avoids redundant LLM calls for similar queries
- Supports cache expiration
- Global singleton instance

---

## End-to-End Process Walkthrough

### Step 1: Data Ingestion
**Component:** `DataIngestionService` in `data_ingestion.py`

The system accepts multiple source types and converts them into normalized chunks:

```python
# Example: Processing different source types
sources = [
    {"type": "pdf", "path": "./data/report.pdf"},
    {"type": "web", "url": "https://example.com/article"},
    {"type": "json", "path": "./data/logs.json"},
    {"type": "text", "path": "./data/document.txt"}
]

# Each source is processed and split into chunks:
# {
#   "content": "chunk text content...",
#   "source": "report.pdf",
#   "chunk_id": "pdf-0001",
#   "source_type": "pdf"
# }
```

**Output:** List of ingested chunks with source metadata

---

### Step 2: Semantic Deduplication
**Component:** `EmbeddingService` in `embedding_service.py`

Chunks are compared using embeddings to detect and merge duplicates:

```
Chunk 1: "The company reported Q3 revenue of $50M"
Chunk 2: "Q3 revenue was $50M according to the company"
         ↓
    [Generate embeddings]
         ↓
    Cosine Similarity: 0.92 (> 0.85 threshold)
         ↓
    MERGED: Duplicate detected, sources tracked
```

**Process:**
- Generate vector embeddings for all chunks (Sentence Transformers)
- Compute pairwise cosine similarity
- Merge chunks with similarity ≥ 0.85
- Track all sources for merged chunks
- Result: Clean, deduplicated chunk list

**Output:** Deduplicated chunks with source tracking

---

### Step 3: Fact Extraction by Researcher Agent
**Component:** `ResearcherAgent` in `researcher_agent.py`

For each deduplicated chunk, the Researcher Agent extracts structured facts:

```python
# Input chunk:
chunk = {
    "content": "Apple Inc. reported record Q3 earnings of $83.03 billion in 2023...",
    "chunk_id": "pdf-0045"
}

# Agent extracts facts:
{
    "facts": [
        "Company: Apple Inc.",
        "Metric: Q3 earnings",
        "Value: $83.03 billion",
        "Year: 2023"
    ],
    "entities": {
        "organizations": ["Apple Inc."],
        "numbers": ["$83.03 billion", "2023"]
    },
    "summary": "Apple's financial performance in Q3 2023",
    "chunk_id": "pdf-0045",
    "cached": false  # Indicates if result came from cache
}
```

**Process:**
- Uses Google Gemini API to analyze each chunk
- Extracts: key facts, entities, dates, numbers
- Generates concise summaries
- Results are cached (keyed by content hash) to avoid duplicate API calls
- If similar chunk processed before, returns cached result immediately

**Output:** Structured fact extraction for all chunks

---

### Step 4: Fact Verification by Critic Agent
**Component:** `CriticAgent` in `critic_agent.py`

The Critic Agent cross-verifies facts across all sources:

```python
# Facts to verify:
fact = "Apple Q3 2023 earnings: $83.03 billion"

# Critic checks against all sources:
Source 1 (PDF): "$83.03 billion" ✓ VERIFIED
Source 2 (Web): "$83.0 billion"  ✓ VERIFIED (minor rounding)
Source 3 (JSON): "$85 billion"   ✗ CONTRADICTED

# Result:
{
    "fact": "Apple Q3 2023 earnings: $83.03 billion",
    "status": "contradicted",
    "verified_sources": 2,
    "contradicted_sources": 1,
    "evidence": [
        {"source": "pdf-0045", "content": "$83.03B", "status": "verified"},
        {"source": "web-0023", "content": "$83.0B", "status": "verified"}
    ],
    "contradictions": [
        {"source": "json-0018", "content": "$85B", "status": "contradicted"}
    ]
}
```

**Process:**
- Groups facts by category (financial, technical, dates, etc.)
- For each fact, searches all other sources for confirmation or contradiction
- Marks fact status: `verified | contradicted | unverified`
- Tracks evidence from each source
- Caches verification results for efficiency
- Uses Gemini API for semantic comparison (not exact string matching)

**Output:** Verified facts with contradiction tracking and source evidence

---

### Step 5: Report Synthesis by Synthesizer Agent
**Component:** `SynthesizerAgent` in `synthesizer_agent.py`

The Synthesizer Agent compiles all verified facts into a polished markdown report:

```markdown
# Technical Report: Company Financial Analysis

## Table of Contents
1. Financial Performance
2. Product Information
3. Market Position
4. Key Dates

## Financial Performance

### Q3 2023 Earnings
**Status:** ✓ Verified (2/3 sources)

Apple Inc. reported Q3 2023 earnings of **$83.03 billion**, confirmed by:
- [PDF Report](data/report.pdf#chunk-pdf-0045)
- [Web Article](data/article#chunk-web-0023)

**Note:** One source reported $85B, which contradicts this figure.

### Annual Revenue Trend
**Status:** ✓ Verified

2022: $394.3B → 2023: $383.3B

**Source Citations:**
- [financial_data.json](data/logs.json#chunk-json-0012)

## Contradictions Found
- Contradiction: Q3 2023 earnings reported as both $83.03B and $85B

---

*Report generated on 2024-01-15 15:30:00*
*Total facts verified: 12/15*
*Total sources processed: 3*
```

**Process:**
- Organizes facts by category/topic
- Includes verification status for each fact
- Adds markdown-formatted source citations
- Lists any contradictions found
- Highlights verified vs. unverified facts
- Includes pipeline statistics and metadata

**Output:** Polished, interactive markdown report

---

### Step 6: API Response & Delivery
**Component:** `FastAPI` endpoint in `api.py`

The orchestrator returns complete metadata alongside the report:

```json
{
  "topic": "Company Financial Analysis",
  "report": "[markdown content as shown above]",
  "facts_count": 15,
  "verified_count": 12,
  "pipeline_stats": {
    "ingestion_time_ms": 450,
    "deduplication_time_ms": 320,
    "extraction_time_ms": 2100,
    "verification_time_ms": 1800,
    "synthesis_time_ms": 600,
    "total_time_ms": 5270,
    "chunks_processed": 28,
    "chunks_deduplicated": 24,
    "cache_hits": 5,
    "api_calls": 19
  },
  "generated_at": "2024-01-15T15:30:00"
}
```

---

## Complete Data Flow Diagram

```
┌──────────────────────┐
│   User/API Request   │
│  (sources + topic)   │
└──────────┬───────────┘
           │
           ↓
┌──────────────────────────────────────────┐
│      Data Ingestion Service              │
│  ✓ Load PDFs, web, JSON, text files     │
│  ✓ Split into chunks                     │
│  ✓ Track source metadata                 │
└──────────┬───────────────────────────────┘
           │
           ↓
┌──────────────────────────────────────────┐
│      Embedding Service                   │
│  ✓ Generate embeddings                   │
│  ✓ Detect semantic duplicates            │
│  ✓ Merge while tracking sources          │
└──────────┬───────────────────────────────┘
           │
           ↓
       [Chunks]
         │ ├─ Cache Lookup
         │ └─ Hit/Miss
         │
    ┌────┴──────────────────────────┐
    │                               │
    ↓                               ↓
[Cache Hit]              [Researcher Agent]
  Return                  ✓ Extract facts
  cached result          ✓ Identify entities
                         ✓ Cache result
                               │
                               ↓
                         [Extracted Facts]
                               │
                               ↓
                       [Critic Agent]
                      ✓ Verify across sources
                      ✓ Find contradictions
                      ✓ Mark status
                               │
                               ↓
                     [Verified Facts + Status]
                               │
                               ↓
                     [Synthesizer Agent]
                    ✓ Organize by category
                    ✓ Add citations
                    ✓ Format markdown
                               │
                               ↓
                    [Final Markdown Report]
                               │
                               ↓
                         [API Response]
                     {report, stats, metadata}
                               │
                               ↓
                     [User/Application]
                    (Downloaded or displayed)
```

---

## Tech Stack

### Core Framework
- **Python 3.11+**
- **LangChain** - LLM orchestration and agent framework
- **FastAPI** - High-performance REST API
- **Streamlit** - Interactive web interface

### AI/ML
- **Google Gemini API** - LLM for fact extraction, verification, synthesis
- **Sentence Transformers** - Semantic embeddings (all-MiniLM-L6-v2)
- **HuggingFace** - Embedding model provider

### Data Processing
- **PDFPlumber** - PDF extraction
- **LangChain Document Loaders** - Multi-format support
- **Requests** - Web scraping

### Caching & Performance
- **DiskCache** - Distributed cache layer (or in-memory fallback)
- **asyncio** - Async/await for concurrent processing

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration

---

## Project Structure

```
problem3_multiagent/
│
├── app/
│   ├── __init__.py
│   ├── log_config.py              # Shared logging configuration
│   ├── cache_manager.py           # DiskCache-based caching layer
│   ├── embedding_service.py       # Semantic embeddings & deduplication
│   ├── data_ingestion.py          # Multi-source data loading
│   ├── researcher_agent.py        # Fact extraction agent
│   ├── critic_agent.py            # Fact verification agent
│   ├── synthesizer_agent.py       # Report compilation agent
│   ├── orchestrator.py            # Multi-agent coordinator
│   ├── api.py                     # FastAPI backend
│   └── streamlit_app.py           # Streamlit frontend
│
├── data/                          # Input documents and logs
├── logs/                          # Runtime logs (multiagent.log)
├── cache/                         # Cached embeddings and LLM results
│
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
├── docker-compose.yml             # Multi-container setup
├── Dockerfile                     # API container
├── Dockerfile.streamlit           # Frontend container
└── README.md                      # This file
```

---

## Setup Instructions

### Prerequisites

- **Python 3.11+**
- **Google Gemini API Key** (get from [Google AI Studio](https://aistudio.google.com/))
- **Git** (optional)

### Local Setup

#### 1. Clone/Navigate to Project
```bash
cd problem3_multiagent
```

#### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

Edit `.env`:
```env
GEMINI_API_KEY=your-actual-gemini-api-key
GEMINI_MODEL_NAME=gemini-2.5-flash
API_URL=http://localhost:8000
```

#### 5. Create Sample Data Directory
```bash
mkdir -p data
# Place your PDF files, JSON logs, or text files here
```

#### 6. Run the Backend API
```bash
uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload
```

Backend available at: `http://localhost:8000`

#### 7. Run the Streamlit Frontend (in another terminal)
```bash
streamlit run app/streamlit_app.py
```

Frontend available at: `http://localhost:8501`

---

## Docker Setup

### Build and Run with Docker Compose

```bash
docker-compose up --build
```

This starts:
- **API Backend**: http://localhost:8000
- **Streamlit Frontend**: http://localhost:8501
- **Shared volumes**: `data/`, `logs/`, `cache/`

### API Documentation

When running, visit: `http://localhost:8000/docs` for interactive API documentation

---

## Step-by-Step Usage Guide

### Option 1: Using Streamlit Web Interface (Recommended for beginners)

#### Setup
1. **Install and activate environment**
   ```bash
   cd problem3_multiagent
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure API key**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY from https://aistudio.google.com/
   ```

3. **Start the backend API** (Terminal 1)
   ```bash
   uvicorn app.api:app --reload
   # Server runs at http://localhost:8000
   ```

4. **Start Streamlit frontend** (Terminal 2)
   ```bash
   streamlit run app/streamlit_app.py
   # UI opens at http://localhost:8501
   ```

#### Using the UI
1. Open browser to `http://localhost:8501`
2. Enter a **Report Topic** (e.g., "Cloud Security Best Practices")
3. **Add Sources** in the sidebar:
   - Text file: Click "Add Text File" → Enter path like `./data/sample_document.txt`
   - PDF: Click "Add PDF" → Enter path like `./data/report.pdf`
   - Web link: Click "Add Web Link" → Enter URL
   - JSON logs: Click "Add JSON" → Enter path like `./data/events.json`
4. Click **"🚀 Generate Report"**
5. View the generated report with citations
6. Click **"Download Report"** to save as markdown

### Option 2: Using REST API (For integration)

#### Example: Generate Report via curl

```bash
# 1. Start the backend (as shown above)

# 2. Make API request
curl -X POST http://localhost:8000/generate-report \
  -H "Content-Type: application/json" \
  -d '{
    "sources": [
      {
        "type": "text",
        "path": "./data/sample_document.txt"
      },
      {
        "type": "json",
        "path": "./data/sample_events.json"
      }
    ],
    "topic": "Technology Trends 2024"
  }'

# 3. Response includes:
# - topic: Your report topic
# - report: Full markdown report with citations
# - facts_count: Total facts extracted
# - verified_count: Facts verified across sources
# - pipeline_stats: Performance metrics
# - generated_at: Timestamp
```

#### Example: Generate Report via Python

```python
import requests
import json

# API endpoint
url = "http://localhost:8000/generate-report"

# Request payload
payload = {
    "sources": [
        {
            "type": "text",
            "path": "./data/sample_document.txt"
        },
        {
            "type": "json",
            "path": "./data/sample_events.json"
        }
    ],
    "topic": "Data Analysis Report"
}

# Make request
response = requests.post(url, json=payload)
result = response.json()

# Access results
print(f"Topic: {result['topic']}")
print(f"Facts verified: {result['verified_count']}/{result['facts_count']}")
print("\nReport:\n")
print(result['report'])

# Save report
with open("output_report.md", "w") as f:
    f.write(result['report'])
```

#### Example: Generate Report via JavaScript/Node.js

```javascript
async function generateReport() {
  const payload = {
    sources: [
      {
        type: "text",
        path: "./data/sample_document.txt"
      },
      {
        type: "json",
        path: "./data/sample_events.json"
      }
    ],
    topic: "Market Analysis Report"
  };

  const response = await fetch("http://localhost:8000/generate-report", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const result = await response.json();
  console.log(`Report topic: ${result.topic}`);
  console.log(`Verified facts: ${result.verified_count}/${result.facts_count}`);
  console.log(`\nReport:\n${result.report}`);
  
  return result;
}

generateReport();
```

### Option 3: Using Docker (For production deployment)

#### Quick Docker setup

```bash
# 1. Build and run
docker-compose up --build

# 2. Access services
# API: http://localhost:8000
# UI: http://localhost:8501
# API Docs: http://localhost:8000/docs

# 3. Make requests (same as curl/Python examples above)
```

#### Using Docker with custom data

```bash
# 1. Place your files in data/ directory
cp /path/to/your/document.pdf ./data/
cp /path/to/your/data.json ./data/

# 2. Run Docker
docker-compose up --build

# 3. Access and use as above
```

---

## Complete Workflow Example

### Scenario: Analyzing a Company's Financial Reports

#### Step 1: Prepare data files
```bash
# Create data directory
mkdir -p data

# Add sample files (or your own)
# - data/annual_report_2023.pdf
# - data/financial_metrics.json
# - data/market_analysis.txt
```

#### Step 2: Start services
```bash
# Terminal 1: Start API
uvicorn app.api:app --reload

# Terminal 2: Start UI
streamlit run app/streamlit_app.py
```

#### Step 3: Generate report via UI
- Open http://localhost:8501
- Topic: "2023 Financial Analysis"
- Add sources:
  - PDF: `./data/annual_report_2023.pdf`
  - JSON: `./data/financial_metrics.json`
  - Text: `./data/market_analysis.txt`
- Click "Generate Report"

#### Step 4: Review results
```markdown
# 2023 Financial Analysis

## Executive Summary
[Synthesized overview from all sources]

## Revenue Analysis
- 2023 Revenue: $1.2B ✓ Verified (2 sources)
- YoY Growth: +15% ✓ Verified (2 sources)
- [Source citations with chunk IDs]

## Profit Margins
- Gross Margin: 42% ✓ Verified
- Operating Margin: 18% ✗ Contradicted (see contradictions)
  - Source 1: 18%
  - Source 2: 16%

## Key Metrics
[All organized by category with verification status]

## Contradictions Found
- Operating margin reported as 18% and 16%
  [Details and sources]

---
Report stats: 24 facts verified, 2 contradictions detected
Processing time: 12.5 seconds
```

---

## API Endpoints

### POST `/generate-report`
Generate a comprehensive report from multiple sources.

**Request:**
```json
{
  "sources": [
    {
      "type": "pdf",
      "path": "/path/to/document.pdf"
    },
    {
      "type": "web",
      "url": "https://example.com/article"
    },
    {
      "type": "json",
      "path": "/path/to/data.json"
    }
  ],
  "topic": "Cloud Security Best Practices"
}
```

**Response:**
```json
{
  "topic": "Cloud Security Best Practices",
  "report": "# Cloud Security Best Practices\n\n## Executive Summary\n...",
  "facts_count": 42,
  "verified_count": 38,
  "generated_at": "2024-05-14T10:30:00",
  "pipeline_stats": {
    "ingestion_time_ms": 450,
    "deduplication_time_ms": 320,
    "extraction_time_ms": 2100,
    "verification_time_ms": 1800,
    "synthesis_time_ms": 600,
    "total_time_ms": 5270,
    "chunks_processed": 28,
    "chunks_deduplicated": 24,
    "cache_hits": 5,
    "api_calls": 19
  }
}
```

### GET `/health`
Check API status.

**Response:**
```json
{
  "status": "healthy",
  "service": "multi-agent-synthesizer"
}
```

---

## Understanding Report Output

### Verification Status Indicators

Each fact in the report shows one of three statuses:

| Status | Symbol | Meaning | Example |
|--------|--------|---------|---------|
| **Verified** | ✓ | Fact confirmed by 2+ sources | ✓ Company founded in 1998 (3 sources) |
| **Contradicted** | ✗ | Sources disagree | ✗ Revenue reported as $50M and $55M |
| **Unverified** | ? | Found in only 1 source | ? CEO speaks 5 languages (1 source) |

### Source Citation Format

```markdown
- [**PDF Report**](data/report.pdf#chunk-pdf-0045) - "Company revenue grew 15%"
- [**Web Article**](data/article#chunk-web-0023) - "Revenue increased by 15%"
```

Click links to view the exact text source and chunk ID for traceability.

### Pipeline Statistics Breakdown

```json
"pipeline_stats": {
  "input_chunks": 156,              // Total chunks after ingestion
  "deduplicated_chunks": 142,       // After removing near-duplicates
  "facts_extracted": 50,             // Facts pulled by Researcher Agent
  "facts_verified": 42,              // Facts with verification status
  "ingestion_time_ms": 450,          // Time to load & split sources
  "deduplication_time_ms": 320,      // Time to find & merge duplicates
  "extraction_time_ms": 2100,        // Time for Researcher Agent
  "verification_time_ms": 1800,      // Time for Critic Agent
  "synthesis_time_ms": 600,          // Time for Synthesizer Agent
  "cache_hits": 5                    // Number of cached results used
}
```

**What it means:**
- High cache hits = Good performance on repeated analyses
- High verification rate (42/50 = 84%) = Strong consensus across sources
- Low deduplication count = Diverse, non-repetitive sources

### Contradictions Section Example

```markdown
## Contradictions Found

### Q3 2023 Revenue
- **Source A** (annual_report.pdf): $83.03 billion
- **Source B** (web_article): $85 billion
- **Impact**: 2% discrepancy, investigate further

### Market Share Estimate
- **Source A** (market_data.json): 18%
- **Source B** (analyst_report): 22%
- **Impact**: 4% difference, unclear methodology
```

This alerts you to verify manually which source is more reliable.

---



---

## Key Features Summary

✅ **Multi-Source Integration** - PDFs, web links, JSON logs, text files  
✅ **Semantic Deduplication** - Eliminate redundant information  
✅ **Fact Extraction** - AI-powered information extraction  
✅ **Cross-Source Verification** - Identify contradictions  
✅ **Smart Caching** - DiskCache reduces LLM API calls  
✅ **Source Citation Engine** - Track facts back to source chunks  
✅ **Async Pipeline** - Non-blocking multi-agent orchestration  
✅ **Docker Support** - Easy deployment  
✅ **Web UI** - Interactive Streamlit interface  
✅ **REST API** - Programmatic access  

---

## Performance & Caching

The system implements intelligent caching to reduce costs:

- **Fact Extraction**: Results cached by content hash (24h default)
- **Verification**: Cached by fact + source combination
- **Report Synthesis**: Cached by topic + fact count
- **Embeddings**: In-memory with DiskCache persistence

**Benefits:**
- First report on new sources: ~15-30 seconds
- Subsequent reports on similar content: ~2-5 seconds (cached)
- Reduced Gemini API calls by 60-80%

---

## Logging

All activity logged to: `logs/multiagent.log`

**Log levels:** INFO (default), WARNING, ERROR

**Includes:**
- Timestamps and module names
- Pipeline progress tracking
- Chunk processing details
- Agent operation summaries
- Error messages and warnings

**View logs:**
```bash
tail -f logs/multiagent.log
```

---

## Troubleshooting & FAQ

### Setup Issues

**Q: "ModuleNotFoundError: No module named 'diskcache'"**
```bash
A: Install missing dependencies:
   pip install diskcache
   # Or reinstall all:
   pip install -r requirements.txt --force-reinstall
```

**Q: "GEMINI_API_KEY not valid"**
```bash
A: 1. Get key from https://aistudio.google.com/
   2. Copy to .env file: GEMINI_API_KEY=your-key
   3. Restart the API server
```

**Q: "Port 8000 already in use"**
```bash
# Option 1: Kill existing process
lsof -ti:8000 | xargs kill -9

# Option 2: Use different port
uvicorn app.api:app --port 8001
```

### Runtime Issues

**Q: "PDFPlumber extraction errors"**
```bash
A: 1. Try Docker (cleaner environment):
      docker-compose up --build
   2. Or install system dependency:
      sudo apt-get install libpoppler-cpp-dev
```

**Q: "Streamlit not connecting to API"**
```bash
A: 1. Verify API is running: curl http://localhost:8000/health
   2. Check .env API_URL: should be http://localhost:8000
   3. Restart Streamlit app
```

**Q: "Report generation is slow"**
```bash
A: This is normal for:
   - First report on new sources (API calls to Gemini)
   - Large documents (100+ pages)
   - Many sources being processed
   
   Cache improves subsequent runs significantly.
```

**Q: "Cache seems to be stale"**
```bash
A: Clear cache with:
   # Via curl
   curl http://localhost:8000/cache/clear
   
   # Via terminal
   rm -rf cache/
   
   # Via Docker
   docker-compose down -v
```

### Performance Questions

**Q: How long should report generation take?**
```
A: Typical times:
   - 1 source (5 pages): 10-15 seconds
   - 3 sources (20 pages): 20-30 seconds
   - Repeated topic: 2-5 seconds (cached)
```

**Q: How many API calls does it make?**
```
A: Depends on content:
   - 10 chunks: ~12 API calls
   - 50 chunks: ~45 API calls
   - Results are cached, so second run: ~2 calls
```

**Q: Can I use this with custom LLM models?**
```
A: Currently supports Google Gemini only.
   To extend: Modify app/researcher_agent.py,
   app/critic_agent.py, app/synthesizer_agent.py
```

### Docker Issues

**Q: "docker-compose: command not found"**
```bash
A: Install Docker Compose:
   # macOS/Linux with Docker Desktop: included
   # Manual install:
   curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
     -o /usr/local/bin/docker-compose
   chmod +x /usr/local/bin/docker-compose
```

**Q: "Permission denied: docker"**
```bash
A: Add user to docker group:
   sudo usermod -aG docker $USER
   newgrp docker
```

**Q: "Cannot connect to Docker daemon"**
```bash
A: Start Docker:
   # macOS: open -a Docker
   # Linux: sudo systemctl start docker
   # Windows: Start Docker Desktop from applications
```

---

## Advanced Usage

### Customizing Chunk Size

Edit `app/data_ingestion.py`:
```python
CHUNK_SIZE = 500        # Current: 500 characters
CHUNK_OVERLAP = 50      # Current: 50 characters

# For better context preservation:
CHUNK_SIZE = 1000       # Larger chunks
CHUNK_OVERLAP = 100     # More overlap

# For faster processing:
CHUNK_SIZE = 250        # Smaller chunks
CHUNK_OVERLAP = 25      # Less overlap
```

### Changing Deduplication Threshold

Edit `app/embedding_service.py`:
```python
SIMILARITY_THRESHOLD = 0.85  # Current: 0.85

# More aggressive deduplication:
SIMILARITY_THRESHOLD = 0.90  # Stricter matching

# Less aggressive:
SIMILARITY_THRESHOLD = 0.75  # More tolerant
```

### Using Custom Embedding Model

Edit `app/embedding_service.py`:
```python
# Current model:
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# Alternatives:
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"       # Larger, more accurate
EMBEDDING_MODEL = "sentence-transformers/paraphrase-MiniLM-L6-v2" # Better paraphrase detection
```

### Setting Cache Expiration

Edit `app/cache_manager.py`:
```python
# Current: 24 hours
cache.set(key, value, expire=86400)

# Change to 7 days:
cache.set(key, value, expire=604800)

# No expiration:
cache.set(key, value)
```

---

## Future Enhancements

- 🔄 Redis support for distributed caching
- 📊 Fact confidence scoring and weighting
- 🌐 Support for multiple languages
- 🔐 Source authentication and access control
- 📈 Report analytics and insights
- 🤝 Multi-turn fact negotiation between agents
- 🎨 HTML/PDF report export options
- ⚡ Streaming report generation for large sources
- 🧠 Fine-tuned models for domain-specific fact extraction
- 📱 Mobile app integration

---

## License

This project is part of an assessment exercise.

---

## Support & Questions

For detailed documentation on each component:
- See `CONFIG.md` for configuration reference
- See `PROJECT_SUMMARY.md` for architecture overview
- See `QUICKSTART.md` for quick setup

For issues:
1. Check logs: `tail -f logs/multiagent.log`
2. Check troubleshooting section above
3. Review API docs: `http://localhost:8000/docs`

---

## Architecture Diagram

```
                    ┌──────────────────┐
                    │   User Request   │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │  Orchestrator    │
                    │  (Main Pipeline) │
                    └────────┬─────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   ┌─────────┐         ┌──────────┐        ┌──────────┐
   │Ingestion│         │Embeddings│        │  Cache   │
   │Service  │         │Service   │        │ Manager  │
   └────┬────┘         └────┬─────┘        └──────┬───┘
        │                   │                     │
        └───────────────────┼─────────────────────┘
                            │
                    ┌───────▼──────┐
                    │Deduplicated  │
                    │  Chunks      │
                    └───────┬──────┘
                            │
                ┌───────────┼───────────┐
                │           │           │
        ┌───────▼─┐   ┌─────▼────┐ ┌───▼──────┐
        │Researcher│   │Critic    │ │Synthesizer│
        │ Agent    │   │ Agent    │ │  Agent    │
        └────┬────┘   └─────┬────┘ └──┬────────┘
             │              │         │
             └──────────────┼─────────┘
                            │
                    ┌───────▼──────┐
                    │Final Report  │
                    │+ Citations   │
                    └──────────────┘
```

---

**Built with ❤️ using LangChain, Google Gemini, and FastAPI**
