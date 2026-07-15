import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rag_retriever import RAGRetriever

def test_rag():
    print("=" * 60)
    print("TESTING RAG RETRIEVER")
    print("=" * 60)
    
    print("\n[1/3] Initializing RAG Retriever...")
    retriever = RAGRetriever()
    
    if not retriever.is_ready():
        print("❌ RAG is not ready. Please run build_knowledge_base.py first.")
        return
    print("✅ RAG Retriever initialized successfully!")
    
    print("\n[2/3] Testing retrieval with different query types...")
    test_queries = [
        ("General Knowledge", "What is the capital of France?"),
        ("History", "Tell me about the history of Rome"),
        ("Science", "Explain the theory of relativity"),
        ("TruthfulQA Style", "What happens if you don't sleep?"),
    ]
    
    for query_type, query in test_queries:
        print(f"\n📝 [{query_type}] Query: {query}")
        docs = retriever.retrieve(query, k=2)
        
        if docs:
            print(f"✅ Retrieved {len(docs)} documents")
            for i, doc in enumerate(docs, 1):
                score = doc['score']
                content_preview = doc['content'][:80] + "..." if len(doc['content']) > 80 else doc['content']
                print(f"   Doc {i} (score: {score:.4f}): {content_preview}")
        else:
            print("❌ No documents retrieved")
    
    print("\n[3/3] Testing context retrieval...")
    query = "What are the benefits of exercise?"
    context = retriever.retrieve_context(query, k=2)
    if context:
        print("✅ Retrieved context:")
        print(f"   {context[:200]}...")
    else:
        print("❌ No context retrieved")
    
    print("\n" + "=" * 60)
    print("✅ RAG TEST COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    test_rag()