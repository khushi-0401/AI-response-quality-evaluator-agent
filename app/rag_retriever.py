# ==============================================================================
# RAG RETRIEVER - Context Retrieval from ChromaDB
# ==============================================================================

import os
import logging
from typing import List, Dict, Any, Optional

# =============================================
# SKIP RAG - Set to True to start server faster
# =============================================
SKIP_RAG = True  # ← Set to False to enable RAG

# =============================================

logger = logging.getLogger(__name__)

class RAGRetriever:
    """Retrieve relevant context from the knowledge base"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.vector_store = None
        self.embeddings = None
        
        # If SKIP_RAG is True, don't load the model
        if SKIP_RAG:
            logger.warning("⚠️ RAG DISABLED - Server will start fast")
            logger.info("✅ To enable RAG, set SKIP_RAG = False in rag_retriever.py")
            return
        
        self._initialize()
    
    def _initialize(self):
        """Initialize the vector store and embeddings"""
        try:
            # Check if the vector store exists
            if not os.path.exists(self.persist_directory):
                logger.warning(f"Vector store not found at {self.persist_directory}")
                logger.info("Please run build_knowledge_base.py first")
                return
            
            from langchain_chroma import Chroma
            from langchain_huggingface import HuggingFaceEmbeddings
            
            # Initialize embeddings
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            
            # Load the vector store
            self.vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embeddings
            )
            
            count = self.vector_store._collection.count()
            logger.info(f"RAGRetriever initialized with {count} documents")
            
        except Exception as e:
            logger.error(f"Error initializing RAGRetriever: {e}")
            self.vector_store = None
    
    def retrieve(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query"""
        if not self.vector_store:
            if SKIP_RAG:
                logger.warning("RAG is disabled. Set SKIP_RAG=False to enable.")
            else:
                logger.warning("Vector store not available.")
            return []
        
        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            
            retrieved_docs = []
            for doc, score in results:
                retrieved_docs.append({
                    'content': doc.page_content,
                    'metadata': doc.metadata,
                    'score': score
                })
            
            logger.info(f"Retrieved {len(retrieved_docs)} documents for query")
            return retrieved_docs
            
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []
    
    def retrieve_context(self, query: str, k: int = 3) -> str:
        """Retrieve and combine context from relevant documents"""
        docs = self.retrieve(query, k)
        if not docs:
            return ""
        
        context_parts = []
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"[Document {i}]\n{doc['content']}")
        
        return "\n\n".join(context_parts)
    
    def is_ready(self) -> bool:
        """Check if the retriever is ready to use"""
        if SKIP_RAG:
            return False
        return self.vector_store is not None