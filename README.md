# AI-Powered Research Assistant

A production-grade RAG (Retrieval-Augmented Generation) system demonstrating real ML engineering practices. Built for AI Engineer portfolios.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Backend                          │
├──────────────────┬──────────────────┬──────────────────────┤
│ Document Service │ Embedding Service│  Search Service       │
│ • Chunking       │ • Transformers   │  • Vector Similarity  │
│ • Validation     │ • Batch Process  │  • Result Ranking     │
└──────────────────┴──────────────────┴──────────────────────┘
         │                   │                    │
         └───────────────────┴────────────────────┘
                             │
                    ┌────────▼────────┐
                    │   ChromaDB      │
                    │ Vector Storage  │
                    └─────────────────┘
```

## Features (Phase 1)

✅ **Document Ingestion**
- Semantic chunking with sentence-aware splitting
- Overlap for context preservation
- Support for text files (.txt, .md)

✅ **Embedding Generation**
- sentence-transformers (all-MiniLM-L6-v2)
- Batch processing
- GPU acceleration support

✅ **Vector Search**
- ChromaDB for persistent storage
- Cosine similarity ranking
- Configurable thresholds

✅ **Extractive Summarization**
- Query-focused sentence selection
- Diversity-aware ranking (MMR-like)
- Maintains document order

✅ **Production-Ready API**
- FastAPI with automatic docs
- Request validation (Pydantic)
- Error handling & logging
- Health monitoring

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.10+, FastAPI |
| Embeddings | sentence-transformers |
| Vector DB | ChromaDB |
| ML Framework | PyTorch |
| API Docs | OpenAPI/Swagger |

## Installation

### Prerequisites
- Python 3.10 or higher
- pip
- 4GB+ RAM (for embedding model)

### Setup

```bash
# Clone repository
git clone <your-repo-url>
cd research-assistant

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# (Optional) Edit .env for custom configuration
nano .env
```

### Download NLTK Data (for summarization)

```python
# Run once
python -c "import nltk; nltk.download('punkt')"
```

## Running the Application

### Development Mode

```bash
# Start server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
# Start server
python -m app.main
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Usage Examples

### 1. Health Check

```bash
curl http://localhost:8000/health
```

### 2. Ingest Document (Text)

```bash
curl -X POST "http://localhost:8000/ingest/text" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Artificial intelligence is transforming healthcare...",
    "filename": "ai_healthcare.txt"
  }'
```

### 3. Ingest Document (File Upload)

```bash
curl -X POST "http://localhost:8000/ingest/file" \
  -F "file=@document.txt"
```

### 4. Semantic Search

```bash
curl -X POST "http://localhost:8000/query/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How is AI used in medical diagnosis?",
    "top_k": 5,
    "score_threshold": 0.3,
    "include_summary": true
  }'
```

### 5. Get Document Chunks

```bash
curl "http://localhost:8000/query/documents/{document_id}"
```

### Python Client Example

```python
import requests

BASE_URL = "http://localhost:8000"

# Ingest document
response = requests.post(
    f"{BASE_URL}/ingest/text",
    json={
        "content": "Your document text here...",
        "filename": "example.txt"
    }
)
doc_id = response.json()["document_id"]

# Search
response = requests.post(
    f"{BASE_URL}/query/search",
    json={
        "query": "your search query",
        "top_k": 5,
        "include_summary": True
    }
)
results = response.json()
print(f"Found {results['total_results']} results")
print(f"Summary: {results['summary']}")
```

## Configuration

Edit `.env` file to customize:

```ini
# Embedding Model (choose based on speed vs quality)
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2  # Fast, 384d
# EMBEDDING_MODEL_NAME=sentence-transformers/all-mpnet-base-v2  # Better, 768d

# Document Processing
CHUNK_SIZE=512              # Characters per chunk
CHUNK_OVERLAP=128           # Overlap between chunks

# Search
SEARCH_TOP_K=5              # Default results to return
SEARCH_SCORE_THRESHOLD=0.3  # Minimum similarity score

# Performance
EMBEDDING_DEVICE=cpu        # Use "cuda" for GPU
EMBEDDING_BATCH_SIZE=32
```

## Project Structure

```
research-assistant/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── api/
│   │   └── routes/          # API endpoints
│   │       ├── ingest.py    # Document ingestion
│   │       ├── query.py     # Search endpoints
│   │       └── health.py    # Health checks
│   ├── core/                # Core ML components
│   │   ├── chunking.py      # Text chunking
│   │   ├── embedding.py     # Embedding generation
│   │   └── summarization.py # Extractive summarization
│   ├── services/            # Business logic
│   │   ├── document_service.py
│   │   └── search_service.py
│   ├── models/
│   │   └── schemas.py       # Pydantic models
│   └── utils/
│       ├── logger.py
│       └── exceptions.py
├── data/                    # Data directory (created at runtime)
│   ├── documents/           # Uploaded documents
│   └── chroma_db/           # Vector database
├── logs/                    # Application logs
├── requirements.txt
└── README.md
```

## Testing

```bash
# Run tests (Phase 2+)
pytest tests/

# With coverage
pytest tests/ --cov=app --cov-report=html
```

## Performance Benchmarks

**Hardware**: Intel i7, 16GB RAM, CPU-only

| Operation | Time | Notes |
|-----------|------|-------|
| Model Load | ~3s | One-time at startup |
| Chunk 10KB doc | ~50ms | ~20 chunks |
| Embed 20 chunks | ~200ms | Batch processing |
| Search query | ~30ms | With summarization |

## Troubleshooting

### Model Download Issues
```bash
# Manually download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"
```

### ChromaDB Permission Errors
```bash
# Fix permissions
chmod -R 755 data/chroma_db/
```

### Out of Memory
- Reduce `EMBEDDING_BATCH_SIZE` in .env
- Use smaller model: `all-MiniLM-L6-v2` instead of `all-mpnet-base-v2`

## Next Steps (Phase 2+)

- [ ] LLM integration (Ollama + LLaMA/Mistral)
- [ ] Generative summarization
- [ ] PDF/DOCX support
- [ ] User authentication
- [ ] React frontend
- [ ] Docker deployment
- [ ] Fine-tuning pipeline

## License

MIT License - See LICENSE file

## Contributing

This is a portfolio project. For major changes, please open an issue first.

## Author

Your Name - [Your GitHub/LinkedIn]

---

Built with FastAPI, sentence-transformers, and ChromaDB
