# Configuration Reference

This guide explains all environment variables and configuration options for the Multi-Agent Content Synthesizer.

## Environment Variables (.env)

### API Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `GEMINI_API_KEY` | Required | Your Google Gemini API key from https://aistudio.google.com/ |
| `GEMINI_MODEL_NAME` | `gemini-2.5-flash` | Google Gemini model to use for LLM tasks |
| `API_URL` | `http://localhost:8000` | URL of the FastAPI backend |
| `API_HOST` | `0.0.0.0` | Host to bind the API server to |
| `API_PORT` | `8000` | Port for the API server |

### Frontend Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `STREAMLIT_PORT` | `8501` | Port for Streamlit web interface |
| `STREAMLIT_SERVER_ADDRESS` | `0.0.0.0` | Address for Streamlit server |

### Cache Configuration

| Variable | Default | Description |
| `CACHE_DIR` | `./cache` | Directory for DiskCache storage |
| `USE_DISKCACHE` | `true` | Enable/disable persistent caching |
| `REDIS_URL` | Optional | Redis URL for distributed caching (future) |

### Directory Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_DIR` | `./data` | Directory for input documents and data files |
| `LOGS_DIR` | `./logs` | Directory for runtime logs |

## Embedding Service Configuration

Located in `app/embedding_service.py`:

```python
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
SIMILARITY_THRESHOLD = 0.85  # For duplicate detection
```

## Data Ingestion Configuration

Located in `app/data_ingestion.py`:

```python
CHUNK_SIZE = 500          # Characters per chunk
CHUNK_OVERLAP = 50        # Overlap between chunks
```

Adjust these for your document sizes:
- **Small docs**: Reduce to chunk_size=300
- **Large docs**: Increase to chunk_size=1000

## Agent Configuration

### Researcher Agent
- Uses Gemini model specified in `GEMINI_MODEL_NAME`
- Extracts: facts, entities, dates, numbers, summaries
- Results cached by content hash

### Critic Agent
- Verifies facts against source content
- Marks status: `verified | contradicted | unverified`
- Supports cross-source verification

### Synthesizer Agent
- Generates structured markdown reports
- Adds table of contents
- Includes source citations

## Cache Configuration Details

### DiskCache
Default persistent cache with optional expiration:

```python
cache.set(key, value, expire=86400)  # 24 hours
```

### In-Memory Fallback
If DiskCache not installed, uses Python dict (loses cache on restart)

## Docker Environment

In `docker-compose.yml`, services inherit from `.env`:

```yaml
environment:
  - GEMINI_API_KEY=${GEMINI_API_KEY}
  - GEMINI_MODEL_NAME=${GEMINI_MODEL_NAME}
  - API_URL=http://api:8000
```

## Sample .env File

```env
# Google Gemini API
GEMINI_API_KEY=your-actual-key-here
GEMINI_MODEL_NAME=gemini-2.5-flash

# API Server
API_URL=http://localhost:8000
API_HOST=0.0.0.0
API_PORT=8000

# Frontend
STREAMLIT_PORT=8501

# Cache
CACHE_DIR=./cache
USE_DISKCACHE=true

# Directories
DATA_DIR=./data
LOGS_DIR=./logs

# Optional Redis (future)
# REDIS_URL=redis://localhost:6379
```

## Logging Configuration

All modules use Python's logging module configured in `app/log_config.py`:

- **Format**: `timestamp - module - level - message`
- **File**: `logs/multiagent.log`
- **Console**: Simultaneously to stdout
- **Level**: `INFO` (shows INFO, WARNING, ERROR, CRITICAL)

To change log level programmatically:
```python
import logging
logging.getLogger().setLevel(logging.DEBUG)
```

## Performance Tuning

### Cache Optimization
```python
# More aggressive caching (less accurate)
similarity_threshold = 0.80

# More conservative caching (higher accuracy)
similarity_threshold = 0.90
```

### Chunk Size Tuning
```python
# Smaller chunks (finer granularity)
chunk_size = 300
chunk_overlap = 30

# Larger chunks (better context)
chunk_size = 1000
chunk_overlap = 100
```

### Embedding Model Selection
```python
# Faster, smaller model
"all-MiniLM-L6-v2"  (384 dims)

# More accurate, larger model
"all-mpnet-base-v2"  (768 dims)
```

## API Rate Limits

Google Gemini API has rate limits based on your plan:
- **Free tier**: 60 requests/minute
- **Paid tier**: Higher limits

Cache helps stay within limits by reusing results.

## Troubleshooting Configuration Issues

### Issue: Cache not persisting
**Solution**: Verify `USE_DISKCACHE=true` and `CACHE_DIR` is writable

### Issue: API calls too slow
**Solution**: 
- Increase `CHUNK_SIZE` to process fewer chunks
- Enable/check DiskCache is working
- Verify `GEMINI_API_KEY` is valid

### Issue: Memory usage high
**Solution**:
- Reduce `CHUNK_SIZE`
- Limit number of sources
- Use smaller embedding model
- Clear cache: `rm -rf cache/`

### Issue: Inaccurate deduplication
**Solution**:
- Adjust `SIMILARITY_THRESHOLD` up (0.90) for stricter matching
- Or down (0.75) for looser matching

## Advanced Configuration

### Custom Embedding Model

Edit `app/embedding_service.py`:
```python
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
```

Available models: https://huggingface.co/models?library=sentence-transformers

### Custom LLM Provider

Edit agent files to use different LLM:
```python
from langchain_openai import ChatOpenAI

model = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

### Custom Cache Backend

Implement `CacheManager` interface for other backends (Redis, Memcached, etc.)

## Security Considerations

⚠️ **Important**: 
- Never commit `.env` file with actual keys
- Use `.env.example` as template
- Rotate API keys regularly
- Run in isolated environment
- Use environment variables, not hardcoded keys

## Monitoring

Check logs for performance:
```bash
tail -f logs/multiagent.log

# Search for specific agent
grep "researcher_agent" logs/multiagent.log

# Monitor cache hits
grep "Cache HIT" logs/multiagent.log
```

## Default Settings Summary

| Component | Setting | Value |
|-----------|---------|-------|
| Embedding Model | Model | all-MiniLM-L6-v2 |
| Deduplication | Similarity Threshold | 0.85 |
| Chunking | Size | 500 chars |
| Chunking | Overlap | 50 chars |
| Caching | Backend | DiskCache |
| Cache | Default Expiry | None (persistent) |
| Logging | Level | INFO |
| API | Timeout | 300 seconds |

For more details, see `README.md` and `QUICKSTART.md`.
