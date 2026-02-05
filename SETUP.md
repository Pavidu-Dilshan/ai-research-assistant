# Quick Setup & Run Guide

## 1. Install Dependencies

```bash
# Navigate to project directory
cd research-assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Download NLTK data (required for summarization)
python -c "import nltk; nltk.download('punkt')"
```

## 2. Configure Environment

```bash
# Copy example config
cp .env.example .env

# (Optional) Edit configuration
# nano .env
```

## 3. Start the Server

```bash
# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start and display:
```
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

## 4. Test the System

Open a new terminal and run the test script:

```bash
# Make sure server is running first!
python quick_start.py
```

This will:
1. Check server health
2. Ingest 3 sample documents about AI
3. Run 3 test queries
4. Display results and system stats

## 5. Explore the API

Open your browser and visit:

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 6. Common Commands

```bash
# Stop the server
Ctrl + C

# Deactivate virtual environment
deactivate

# View logs
tail -f logs/app.log

# Run tests (after writing more tests)
pytest tests/ -v
```

## Troubleshooting

### Server won't start
- Check if port 8000 is already in use
- Try a different port: `uvicorn app.main:app --port 8001`

### Model download slow
- The first run downloads ~90MB model
- Takes 1-2 minutes on slow connections
- Subsequent runs are instant (model is cached)

### Out of memory
- Reduce batch size in .env: `EMBEDDING_BATCH_SIZE=8`
- Use smaller model (already using smallest)

### Permission denied on data/
```bash
chmod -R 755 data/
```

## Next Steps

1. ✅ You've completed Phase 1!
2. Try ingesting your own documents
3. Experiment with different search parameters
4. Review the code architecture
5. Ready for Phase 2? (LLM integration)

## File Structure Reminder

```
research-assistant/
├── app/              # Application code
├── data/             # Data directory (auto-created)
├── logs/             # Log files (auto-created)
├── tests/            # Test files
├── requirements.txt  # Dependencies
├── README.md         # Full documentation
└── quick_start.py    # Test script
```

## API Quick Reference

```bash
# Health check
curl http://localhost:8000/health

# Ingest document
curl -X POST http://localhost:8000/ingest/text \
  -H "Content-Type: application/json" \
  -d '{"content": "your text", "filename": "doc.txt"}'

# Search
curl -X POST http://localhost:8000/query/search \
  -H "Content-Type: application/json" \
  -d '{"query": "your query", "top_k": 5, "include_summary": true}'
```

---

Questions? Check the full README.md for detailed documentation.
