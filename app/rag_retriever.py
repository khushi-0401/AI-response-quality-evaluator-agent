import os
from typing import List, Dict, Any, Optional
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import logging

logger = logging.getLogger(__name__)

class RAGRetriever:
    """Retrieve relevant context from the knowledge base"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.persist_directory = persist_directory
        self.vector_store = None
        self.embeddings = None
        self._initialize()
    
    def _initialize(self):
        """Initialize the vector store and embeddings"""
        try:
            # Check if the vector store exists
            if not os.path.exists(self.persist_directory):
                logger.warning(f"Vector store not found at {self.persist_directory}")
                logger.info("Please run scripts/build_knowledge_base.py first")
                return
            
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
        """
        Retrieve relevant documents for a query
        
        Args:
            query: The question/query text
            k: Number of documents to retrieve
            
        Returns:
            List of retrieved documents with content and metadata
        """
        if not self.vector_store:
            logger.warning("Vector store not available. Please build the knowledge base first.")
            return []
        
        try:
            # Retrieve similar documents
            results = self.vector_store.similarity_search_with_score(query, k=k)
            
            # Format results
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
        """
        Retrieve and combine context from relevant documents
        
        Returns:
            Combined context string
        """
        docs = self.retrieve(query, k)
        if not docs:
            return ""
        
        # Combine document contents
        context_parts = []
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"[Document {i}]\n{doc['content']}")
        
        return "\n\n".join(context_parts)
    
    def is_ready(self) -> bool:
        """Check if the retriever is ready to use"""
        return self.vector_store is not None