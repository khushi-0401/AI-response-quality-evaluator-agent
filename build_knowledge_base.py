import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datasets import load_dataset
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
import logging
import warnings

# Disable all warnings
warnings.filterwarnings("ignore")
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Suppress datasets warnings
import datasets
datasets.logging.set_verbosity_error()

# Suppress transformers warnings
import transformers
transformers.logging.set_verbosity_error()

logging.basicConfig(level=logging.ERROR)

def build_rag_system():
    print("=" * 60)
    print("BUILDING RAG KNOWLEDGE BASE")
    print("=" * 60)
    
    all_documents = []
    
    # =============================================
    # Step 1: Load SQuAD Dataset (NO trust_remote_code)
    # =============================================
    print("\n[1/4] Fetching SQuAD dataset from Hugging Face...")
    try:
        squad_dataset = load_dataset("rajpurkar/squad", split="train[:50]")
        squad_texts = [item["context"] for item in squad_dataset]
        squad_unique = list(set(squad_texts))
        print(f"✅ Loaded {len(squad_unique)} unique documents from SQuAD")
        all_documents.extend(squad_unique)
    except Exception as e:
        print(f"⚠️ Could not load SQuAD: {e}")
        return
    
    # =============================================
    # Step 2: Load TruthfulQA Dataset (NO trust_remote_code)
    # =============================================
    print("\n[2/4] Fetching TruthfulQA dataset from Hugging Face...")
    try:
        truthful_dataset = load_dataset(
            "truthfulqa/truthful_qa", 
            "generation", 
            split="validation[:50]"
        )
        truthful_texts = []
        for item in truthful_dataset:
            text = f"Question: {item['question']}\nAnswer: {item['best_answer']}"
            truthful_texts.append(text)
        
        print(f"✅ Loaded {len(truthful_texts)} documents from TruthfulQA")
        all_documents.extend(truthful_texts)
    except Exception as e:
        print(f"⚠️ Could not load TruthfulQA: {e}")
        print("   Continuing with SQuAD only...")
    
    # =============================================
    # Step 3: Check if we have any documents
    # =============================================
    if not all_documents:
        print("\n❌ No documents loaded.")
        return
    
    print(f"\n📊 Total documents loaded: {len(all_documents)}")
    
    # =============================================
    # Step 4: Chunking
    # =============================================
    print("\n[3/4] Chunking documents...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, 
        chunk_overlap=50
    )
    chunks = text_splitter.create_documents(all_documents)
    print(f"✅ Created {len(chunks)} text chunks!")
    
    # =============================================
    # Step 5: Embeddings & Vector Store
    # =============================================
    print("\n[4/4] Generating embeddings and saving to ChromaDB...")
    try:
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory="./chroma_db"
        )
        
        print("\n" + "=" * 60)
        print("✅ RAG KNOWLEDGE BASE BUILD COMPLETE!")
        print("=" * 60)
        print(f"📊 Total documents loaded: {len(all_documents)}")
        print(f"📊 Total chunks created: {len(chunks)}")
        print(f"📁 Vector store saved to: ./chroma_db")
        print("\nDatasets included:")
        print("  ✅ SQuAD (context passages)")
        if len(truthful_texts) > 0:
            print("  ✅ TruthfulQA (question-answer pairs)")
        print("\n🚀 You can now use RAG-grounded evaluation in your FastAPI app!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error building vector store: {e}")

if __name__ == "__main__":
    build_rag_system()