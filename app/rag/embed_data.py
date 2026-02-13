"""
Embed processed fitness data using LangChain + Google Gemini embeddings
Uses the officially supported 'models/embedding-001' model
"""
import json
from pathlib import Path
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from app.core.config import settings


def load_processed_data():
    """Load all processed JSON files and convert to LangChain Documents"""
    exercises_file = Path("data/processed/exercises_processed.json")
    pdfs_file = Path("data/processed/pdfs_processed.json")
    
    documents = []
    
    # Load exercises
    if exercises_file.exists():
        print(f"\n📋 Loading exercises from {exercises_file}...")
        with open(exercises_file, 'r', encoding='utf-8') as f:
            exercises = json.load(f)
        
        for item in exercises:
            # Create LangChain Document
            doc = Document(
                page_content=item['text'],
                metadata=item['metadata']
            )
            documents.append(doc)
        
        print(f"✅ Loaded {len(exercises)} exercises")
    else:
        print(f"⚠️  {exercises_file} not found, skipping exercises")
    
    # Load PDFs
    if pdfs_file.exists():
        print(f"\n📄 Loading PDF chunks from {pdfs_file}...")
        with open(pdfs_file, 'r', encoding='utf-8') as f:
            pdf_chunks = json.load(f)
        
        for item in pdf_chunks:
            # Create LangChain Document
            doc = Document(
                page_content=item['text'],
                metadata=item['metadata']
            )
            documents.append(doc)
        
        print(f"✅ Loaded {len(pdf_chunks)} PDF chunks")
    else:
        print(f"⚠️  {pdfs_file} not found, skipping PDFs")
    
    return documents


def embed_and_store():
    """Main function to embed all processed data and store in ChromaDB using LangChain"""
    
    print("=" * 60)
    print("🚀 LangChain + Gemini Embedding Pipeline")
    print("=" * 60)
    
    # Check API key
    if not settings.GEMINI_API_KEY:
        print("❌ Error: GEMINI_API_KEY not found!")
        print("   Add it to your .env file")
        return
    
    # Load processed data
    print("\n📂 Loading processed data...")
    documents = load_processed_data()
    
    if not documents:
        print("\n❌ No documents found to embed!")
        print("   Please run:")
        print("   - python scripts/process_exercises.py")
        print("   - python scripts/process_pdfs.py")
        return
    
    print(f"\n📊 Total documents to embed: {len(documents)}")
    
    # Initialize Gemini embeddings
    print("\n🔧 Initializing Gemini embeddings (gemini-embedding-001)...")
    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001",  # Correct model name for LangChain 4.0.0+
        google_api_key=settings.GEMINI_API_KEY,
        task_type="retrieval_document"  # Optimize for document retrieval
    )
    
    # Initialize ChromaDB
    print("\n🗄️  Initializing ChromaDB...")
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    
    chroma_client = chromadb.PersistentClient(
        path="./data/chroma_db",
        settings=ChromaSettings(anonymized_telemetry=False)
    )
    
    # Delete existing collection if it exists
    try:
        existing_collection = chroma_client.get_collection("fitness_knowledge")
        existing_count = existing_collection.count()
        print(f"   � Found existing collection with {existing_count} documents")
        
        # Ask user if they want to resume or start fresh
        if existing_count > 0:
            print(f"   ♻️  Resuming from document {existing_count + 1}...")
            collection = existing_collection
            start_index = existing_count
        else:
            chroma_client.delete_collection("fitness_knowledge")
            collection = chroma_client.create_collection(
                name="fitness_knowledge",
                metadata={"description": "Fitness exercises and guidelines"}
            )
            print("   ✅ Created new collection: fitness_knowledge")
            start_index = 0
    except:
        # Collection doesn't exist, create new one
        collection = chroma_client.create_collection(
            name="fitness_knowledge",
            metadata={"description": "Fitness exercises and guidelines"}
        )
        print("   ✅ Created new collection: fitness_knowledge")
        start_index = 0
    
    # Process in batches with rate limiting
    # Free tier: 100 requests/minute = ~1.6 requests/second
    # We'll do 50 docs per batch with 30 second delays to be safe
    batch_size = 50
    total_docs = len(documents)
    remaining_docs = total_docs - start_index
    total_batches = (remaining_docs + batch_size - 1) // batch_size
    
    if start_index > 0:
        print(f"\n⏱️  Resuming: Processing {remaining_docs} remaining documents in {total_batches} batches")
    else:
        print(f"\n⏱️  Processing {total_docs} documents in {total_batches} batches of {batch_size}")
    
    print(f"   Estimated time: ~{total_batches * 0.5:.1f} minutes")
    print("   (Rate limited to respect Gemini free tier: 100 requests/min)\n")
    
    import time
    
    for i in range(start_index, total_docs, batch_size):
        batch_num = (i // batch_size) + 1
        batch = documents[i:i+batch_size]
        
        print(f"📦 Batch {batch_num}/{total_batches} ({len(batch)} documents)...")
        
        try:
            # Extract texts and metadatas
            texts = [doc.page_content for doc in batch]
            metadatas = [doc.metadata for doc in batch]
            ids = [f"doc_{i+j}" for j in range(len(batch))]
            
            # Clean metadatas for ChromaDB (convert lists to strings, remove None)
            cleaned_metadatas = []
            for metadata in metadatas:
                cleaned = {}
                for key, value in metadata.items():
                    if value is None:
                        continue
                    elif isinstance(value, list):
                        # Convert list to comma-separated string
                        cleaned[key] = ", ".join(str(v) for v in value)
                    else:
                        cleaned[key] = str(value)
                cleaned_metadatas.append(cleaned)
            
            # Embed the batch
            print(f"   🔄 Embedding...")
            batch_embeddings = embeddings.embed_documents(texts)
            
            # Add to ChromaDB
            print(f"   💾 Storing in ChromaDB...")
            collection.add(
                embeddings=batch_embeddings,
                documents=texts,
                metadatas=cleaned_metadatas,
                ids=ids
            )
            
            print(f"   ✅ Batch {batch_num} complete!")
            
            # Rate limiting: Wait 30 seconds between batches (except last one)
            if batch_num < total_batches:
                print(f"   ⏳ Waiting 30 seconds (rate limit)...\n")
                time.sleep(30)
        
        except Exception as e:
            print(f"   ❌ Error in batch {batch_num}: {e}")
            print(f"   Retrying in 60 seconds...")
            time.sleep(60)
            
            # Retry once
            try:
                batch_embeddings = embeddings.embed_documents(texts)
                collection.add(
                    embeddings=batch_embeddings,
                    documents=texts,
                    metadatas=metadatas,
                    ids=ids
                )
                print(f"   ✅ Batch {batch_num} complete (after retry)!")
                if batch_num < total_batches:
                    time.sleep(30)
            except Exception as retry_error:
                print(f"   ❌ Retry failed: {retry_error}")
                print(f"   Skipping batch {batch_num}")
                continue
    
    # Verify
    count = collection.count()
    
    print("\n" + "=" * 60)
    print("✅ EMBEDDING COMPLETE!")
    print("=" * 60)
    print(f"📍 Location: ./data/chroma_db")
    print(f"📊 Documents: {count}")
    print(f"🔧 Model: gemini-embedding-001 (Gemini)")
    print(f"🎯 Framework: LangChain")
    print("\n💡 You can now use the RAG system in your FastAPI app!")


if __name__ == "__main__":
    embed_and_store()

