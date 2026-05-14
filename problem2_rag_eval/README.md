# RAG Evaluation Tool

## Overview

This project implements a Retrieval-Augmented Generation (RAG) evaluation system with automated hallucination detection and self-correction capabilities.

The system:
- Ingests text documents from Supabase storage or a local folder
- Creates semantic embeddings and persists vectors in ChromaDB
- Retrieves the most relevant context for user queries
- Generates answers using a configured LLM
- Evaluates responses with context relevance, faithfulness, and answer relevance
- Applies a self-correction loop for low-faithfulness answers
- Stores final outputs and evaluation records in a Supabase database table

---

## Architecture

The end-to-end pipeline is built as follows:

1. Document ingestion
   - `app/ingest.py` orchestrates ingestion and indexing
   - `app/rag_pipeline.py` downloads documents from Supabase bucket `Files`
   - if Supabase returns no files, it falls back to a local documents folder using `LOCAL_DOCUMENTS_PATH`
   - text documents are split into smaller chunks for embedding

2. Embedding and vector storage
   - Sentence Transformers generate semantic embeddings
   - embeddings are stored in a local Chroma vector database under `vectordb/`
   - the vector store is persisted so retrieval can reuse indexed data

3. Retrieval and generation
   - user queries are sent through the FastAPI backend (`app/api.py`)
   - the RAG pipeline retrieves the top relevant chunks from Chroma
   - the evaluated LLM answer is generated using the retrieved context

4. Evaluation and self-correction
   - `app/evaluator.py` scores responses on context relevance, faithfulness, and answer relevance
   - if faithfulness is below threshold, `app/self_corrector.py` triggers a stricter grounded regeneration path
   - the final corrected response is returned to the frontend or API client

5. Output storage
   - final answers and evaluation metadata are saved to the Supabase table `rag_final_outputs`
   - this ensures all results are persisted for later inspection and reporting

---

## Features

### Document Ingestion
- Recursive character text splitting
- Local vector database using ChromaDB
- Semantic embeddings using Sentence Transformers

### Retrieval-Augmented Generation
- Semantic similarity search
- Context-aware response generation

### RAG Evaluation Metrics
The system evaluates:
1. Context Relevance
2. Faithfulness
3. Answer Relevance

### Self-Correction Loop
If faithfulness score is low, the system automatically regenerates the answer using stricter grounding instructions.

### Comprehensive Logging
The system includes detailed logging throughout the pipeline:
- Document download and processing
- Chunking and embedding creation
- Vector store operations
- Retrieval of relevant chunks
- Answer generation and evaluation
- Self-correction triggers
- API requests and responses

Logs are formatted with timestamps and module names for easy debugging and monitoring.

---

## Tech Stack

- Python
- LangChain
- ChromaDB
- HuggingFace Sentence Transformers
- Transformers

---

## Project Structure

problem2_rag_eval/
│
├── data/                        # local document storage and fallback source
├── logs/                        # shared runtime log file: logs/app.log
├── vectordb/                    # persisted Chroma vector database
├── app/
│   ├── api.py                   # FastAPI backend for query handling
│   ├── ingest.py                # ingestion and indexing orchestration
│   ├── log_config.py            # shared logger configuration
│   ├── rag_pipeline.py          # download/fallback, embedding, retrieval pipeline
│   ├── evaluator.py             # response evaluation scoring
│   ├── self_corrector.py        # faithfulness-based self-correction logic
│   ├── streamlit_app.py         # Streamlit frontend app
│
├── requirements.txt
└── README.md

---

## Setup Instructions

### Install Dependencies

- Create a `.env` file in the project root with your Supabase settings.
- Run `pip install -r requirements.txt`.

### Supabase configuration

The app uses Supabase for storage and output recording. Set the following values in `.env`:

```env
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_STORAGE_BUCKET=Files
SUPABASE_TABLE_NAME=rag_final_outputs
LOCAL_DOCUMENTS_PATH=C:\Users\<your-user>\AI-Python_Assessment\problem2_rag_eval\data
GEMINI_API_KEY=your-gemini-api-key
GEMINI_MODEL_NAME=gemini-1.5-pro
```

Optional: use `LOCAL_DOCUMENTS_PATH` to supply local `.txt` files when Supabase download is unavailable.

### Run the backend API

Install dependencies and then start the FastAPI server:

```bash
pip install -r requirements.txt
uvicorn app.api:app --host 0.0.0.0 --port 8000
```

### Run document ingestion

Process documents and create the vector store:

```bash
python app/ingest.py
```

### Run the Streamlit UI

Launch the frontend with:

```bash
streamlit run app/streamlit_app.py
```

If you want to configure the API endpoint in Streamlit, set an `API_URL` environment variable.

### Code hygiene

The project follows a modular structure and uses type hints for core functions.

Optional formatting and linting tools:

```bash
black .
flake8 app
```

### Docker compose

Build and start both services with:

```bash
docker-compose up --build
```

The FastAPI API will be available at `http://localhost:8000` and the Streamlit UI at `http://localhost:8501`.


