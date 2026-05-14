# Quick Start Guide - Multi-Agent Content Synthesizer

## 5-Minute Setup

### 1. Prerequisites
```bash
Python 3.11+
Google Gemini API Key (free tier available at https://aistudio.google.com/)
```

### 2. Install & Configure
```bash
# Clone/navigate to project
cd problem3_multiagent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 3. Prepare Sample Data
```bash
# Sample files are provided:
# - data/sample_events.json (JSON logs)
# - data/sample_document.txt (Text content)

# Add your own sources:
# - Place PDFs in data/ folder
# - Reference web URLs in the UI
```

### 4. Run Locally
```bash
# Terminal 1: Start API
uvicorn app.api:app --reload

# Terminal 2: Start Frontend
streamlit run app/streamlit_app.py

# Open browser:
# Frontend: http://localhost:8501
# API Docs: http://localhost:8000/docs
```

### 5. Use the System
1. Open Streamlit at http://localhost:8501
2. Enter report topic: "Sample Analysis Report"
3. Add source: text file at `./data/sample_document.txt`
4. Click "Generate Report"
5. View results and download markdown

## Docker Setup

```bash
# Single command setup
docker-compose up --build

# Services running:
# API: http://localhost:8000
# UI: http://localhost:8501
```

## Next Steps

1. **Replace Sample Data** - Add your own PDFs, web links, and JSON logs
2. **Customize Report Topic** - Define what you want to analyze
3. **Tune Embeddings** - Adjust deduplication threshold (currently 0.85)
4. **Monitor Logs** - Check `logs/multiagent.log` for execution details
5. **API Integration** - Use FastAPI endpoints programmatically

## Troubleshooting

### No module named 'diskcache'
```bash
pip install diskcache
# Or: pip install -r requirements.txt --force-reinstall
```

### Gemini API Key Invalid
- Verify key at https://aistudio.google.com/
- Check .env file syntax
- Restart services after updating .env

### Slow PDF Processing
- Large PDFs require more processing time
- Check `logs/multiagent.log` for progress
- Increase timeout in docker-compose.yml if needed

### Port Already in Use
```bash
# Change API port in .env and docker-compose.yml
# Or kill existing processes:
# Unix: lsof -ti:8000 | xargs kill -9
# Windows: netstat -ano | findstr :8000
```

## Architecture at a Glance

```
User Input → Data Ingestion → Deduplication → Fact Extraction
     ↓                                           ↓
Documents/URLs → Embeddings + Caching ← Researcher Agent
     ↓                                           ↓
Chunks → Verification ← Critic Agent
     ↓                ↓
Facts Verified → Report Synthesis ← Synthesizer Agent
     ↓                                           ↓
Final Report with Citations ← Source Tracking
```

## Key Files

| File | Purpose |
|------|---------|
| `app/api.py` | FastAPI backend with endpoints |
| `app/streamlit_app.py` | Web UI for report generation |
| `app/orchestrator.py` | Main pipeline coordinator |
| `app/researcher_agent.py` | Fact extraction |
| `app/critic_agent.py` | Fact verification |
| `app/synthesizer_agent.py` | Report generation |
| `logs/multiagent.log` | Runtime execution log |

## Performance Tips

1. **Enable Caching** - Keep `USE_DISKCACHE=true` in .env
2. **Batch Processing** - Process multiple sources in one request
3. **Monitor Log File** - Track execution time and cache hits
4. **Adjust Thresholds** - Modify similarity threshold in `embedding_service.py`
5. **Reuse Sources** - Cache improves performance on repeated analyses

## Need Help?

- Check README.md for full documentation
- Review `logs/multiagent.log` for error details
- Visit http://localhost:8000/docs for API documentation
- Examine sample data files in `data/` folder

Happy Report Generating! 🚀
