# RAG Evaluation Tool

## Overview

This project implements a Retrieval-Augmented Generation (RAG) evaluation system with automated hallucination detection and self-correction capabilities.

The system:
- Processes text documents
- Creates semantic embeddings
- Stores vectors in ChromaDB
- Retrieves relevant context for user queries
- Generates answers using an LLM
- Evaluates response quality using RAG triad metrics
- Performs self-correction when faithfulness is low

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
├── data/
├── vectordb/
├── app/
│   ├── ingest.py
│   ├── rag_pipeline.py
│   ├── evaluator.py
│   ├── self_corrector.py
│
├── requirements.txt
└── README.md

---

## Setup Instructions

### Install Dependencies

