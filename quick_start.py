#!/usr/bin/env python3
"""
Quick start script to test the Research Assistant system.
Ingests sample documents and runs test queries.
"""
import asyncio
import httpx
import time

BASE_URL = "http://localhost:8000"

# Sample documents
SAMPLE_DOCS = [
    {
        "filename": "ai_overview.txt",
        "content": """
        Artificial Intelligence (AI) is revolutionizing multiple industries. Machine learning,
        a subset of AI, enables computers to learn from data without explicit programming.
        Deep learning, using neural networks with multiple layers, has achieved breakthrough
        results in image recognition, natural language processing, and game playing.
        
        AI applications include autonomous vehicles, medical diagnosis, financial trading,
        and virtual assistants. However, AI also raises ethical concerns about bias, privacy,
        and job displacement. Responsible AI development requires careful consideration of
        these societal impacts.
        """
    },
    {
        "filename": "ml_techniques.txt",
        "content": """
        Machine learning encompasses various techniques including supervised learning,
        unsupervised learning, and reinforcement learning. Supervised learning uses labeled
        data to train models for classification and regression tasks. Unsupervised learning
        discovers patterns in unlabeled data through clustering and dimensionality reduction.
        
        Popular algorithms include decision trees, random forests, support vector machines,
        and neural networks. Feature engineering and model selection are critical steps in
        building effective ML systems. Cross-validation helps prevent overfitting and ensures
        model generalization.
        """
    },
    {
        "filename": "healthcare_ai.txt",
        "content": """
        AI is transforming healthcare through improved diagnosis, treatment planning, and
        drug discovery. Medical imaging analysis using deep learning can detect diseases
        like cancer earlier and more accurately than traditional methods. Natural language
        processing extracts insights from electronic health records.
        
        AI-powered clinical decision support systems assist doctors in diagnosis and treatment
        recommendations. Predictive analytics identify high-risk patients who need preventive
        care. However, challenges include data privacy, regulatory approval, and ensuring
        AI recommendations are explainable to clinicians.
        """
    }
]

# Test queries
TEST_QUERIES = [
    "What are the main applications of artificial intelligence?",
    "How does machine learning work?",
    "What role does AI play in healthcare?"
]


async def check_health():
    """Check if server is running."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/health", timeout=5.0)
            response.raise_for_status()
            print("✓ Server is running")
            print(f"  Status: {response.json()}")
            return True
        except httpx.RequestError:
            print("✗ Server is not running. Please start the server first:")
            print("  uvicorn app.main:app --reload")
            return False


async def ingest_documents():
    """Ingest sample documents."""
    print("\n" + "="*70)
    print("INGESTING SAMPLE DOCUMENTS")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        doc_ids = []
        
        for doc in SAMPLE_DOCS:
            print(f"\nIngesting: {doc['filename']}")
            
            try:
                response = await client.post(
                    f"{BASE_URL}/ingest/text",
                    json=doc,
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                doc_ids.append(result['document_id'])
                
                print(f"  ✓ Success")
                print(f"    Document ID: {result['document_id']}")
                print(f"    Chunks created: {result['chunks_created']}")
                print(f"    Embedding dimension: {result['embedding_dimension']}")
                
            except httpx.HTTPError as e:
                print(f"  ✗ Failed: {e}")
        
        return doc_ids


async def run_queries():
    """Run test queries."""
    print("\n" + "="*70)
    print("RUNNING TEST QUERIES")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        for query in TEST_QUERIES:
            print(f"\nQuery: {query}")
            print("-" * 70)
            
            try:
                start_time = time.time()
                
                response = await client.post(
                    f"{BASE_URL}/query/search",
                    json={
                        "query": query,
                        "top_k": 3,
                        "include_summary": True
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                
                elapsed = (time.time() - start_time) * 1000
                result = response.json()
                
                print(f"Results: {result['total_results']} chunks found")
                print(f"Processing time: {elapsed:.2f}ms")
                
                if result['summary']:
                    print(f"\nSummary:\n{result['summary']}")
                
                print("\nTop Results:")
                for i, res in enumerate(result['results'][:3], 1):
                    print(f"\n  {i}. Score: {res['score']:.3f}")
                    print(f"     Document: {res['metadata'].get('source', 'N/A')}")
                    print(f"     Text: {res['text'][:200]}...")
                
            except httpx.HTTPError as e:
                print(f"✗ Query failed: {e}")


async def get_stats():
    """Get system statistics."""
    print("\n" + "="*70)
    print("SYSTEM STATISTICS")
    print("="*70)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{BASE_URL}/stats", timeout=5.0)
            response.raise_for_status()
            
            stats = response.json()
            
            print("\nDatabase:")
            for key, value in stats['database'].items():
                print(f"  {key}: {value}")
            
            print("\nEmbedding Model:")
            for key, value in stats['embedding_model'].items():
                print(f"  {key}: {value}")
            
            print("\nConfiguration:")
            for key, value in stats['configuration'].items():
                print(f"  {key}: {value}")
                
        except httpx.HTTPError as e:
            print(f"✗ Failed to get stats: {e}")


async def main():
    """Main test workflow."""
    print("="*70)
    print("AI RESEARCH ASSISTANT - QUICK START TEST")
    print("="*70)
    
    # Check server health
    if not await check_health():
        return
    
    # Ingest documents
    doc_ids = await ingest_documents()
    
    if not doc_ids:
        print("\n✗ No documents were ingested. Exiting.")
        return
    
    # Wait a moment for indexing
    print("\nWaiting for indexing...")
    await asyncio.sleep(2)
    
    # Run queries
    await run_queries()
    
    # Show stats
    await get_stats()
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print("\nNext steps:")
    print("  • Visit http://localhost:8000/docs for interactive API documentation")
    print("  • Ingest your own documents via the API")
    print("  • Experiment with different queries and parameters")
    print("  • Check logs/ directory for detailed application logs")


if __name__ == "__main__":
    asyncio.run(main())
