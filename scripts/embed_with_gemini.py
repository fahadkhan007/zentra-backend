"""
Embed all processed data using Google Gemini API (FREE) and store in ChromaDB
"""
import json
import os
from pathlib import Path
import google.generativeai as genai
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ Error: GEMINI_API_KEY not found in environment variables")
    print("   Please add it to your .env file:")
    print("   GEMINI_API_KEY=your-api-key-here")
    print("\n   Get your FREE API key at: https://aistudio.google.com/app/apikey")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# Initialize ChromaDB
chroma_client = chromadb.PersistentClient(
    path="data/chroma_db",
    settings=Settings(anonymized_telemetry=False)
)


def embed_texts_batch(texts: list[str], batch_size: int = 100) -> list[list[float]]:
    """
    Embed texts using Gemini API in batches
    
    Args:
        texts: List of texts to embed
        batch_size: Number of texts to embed per API call (max 100 for Gemini)
    
    Returns:
        List of embeddings (each embedding is a list of floats)
    """
    all_embeddings = []
    total = len(texts)
    
    print(f"🔢 Embedding {total} texts in batches of {batch_size}...")
    
    for i in range(0, total, batch_size):
        batch = texts[i:i+batch_size]
        batch_num = (i // batch_size) + 1
        total_batches = (total + batch_size - 1) // batch_size
        
        print(f"   Processing batch {batch_num}/{total_batches} ({len(batch)} texts)...")
        
        try:
            # Gemini embedding API
            result = genai.embed_content(
                model="models/text-embedding-004",  # FREE model
                content=batch,
                task_type="retrieval_document"
            )
            
            embeddings = result['embedding']
            
            # If single text, wrap in list
            if not isinstance(embeddings[0], list):
                embeddings = [embeddings]
            
            all_embeddings.extend(embeddings)
            
            # Rate limiting: Gemini free tier allows ~60 requests/min
            # Sleep briefly to avoid hitting limits
            if batch_num < total_batches:
                time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Error embedding batch {batch_num}: {e}")
            print(f"   Retrying in 2 seconds...")
            time.sleep(2)
            
            try:
                result = genai.embed_content(
                    model="models/text-embedding-004",
                    content=batch,
                    task_type="retrieval_document"
                )
                embeddings = result['embedding']
                if not isinstance(embeddings[0], list):
                    embeddings = [embeddings]
                all_embeddings.extend(embeddings)
            except Exception as retry_error:
                print(f"❌ Retry failed: {retry_error}")
                raise
    
    print(f"✅ Embedded {len(all_embeddings)} texts")
    return all_embeddings


def embed_and_store():
    """Main function to embed all processed data and store in ChromaDB"""
    
    print("=" * 60)
    print("🚀 Gemini Embedding Pipeline (100% FREE)")
    print("=" * 60)
    
    # Create or get collection
    collection = chroma_client.get_or_create_collection(
        name="fitness_knowledge",
        metadata={"description": "Fitness exercises and guidelines"}
    )
    
    print(f"\n📚 Using ChromaDB collection: fitness_knowledge")
    
    # Load processed data
    exercises_file = Path("data/processed/exercises_processed.json")
    pdfs_file = Path("data/processed/pdfs_processed.json")
    
    all_documents = []
    all_metadatas = []
    all_ids = []
    
    # Load exercises
    if exercises_file.exists():
        print(f"\n📋 Loading exercises from {exercises_file}...")
        with open(exercises_file, 'r', encoding='utf-8') as f:
            exercises = json.load(f)
        
        for item in exercises:
            all_documents.append(item['text'])
            all_metadatas.append(item['metadata'])
            all_ids.append(item['id'])
        
        print(f"✅ Loaded {len(exercises)} exercises")
    else:
        print(f"⚠️  {exercises_file} not found, skipping exercises")
    
    # Load PDFs
    if pdfs_file.exists():
        print(f"\n📄 Loading PDF chunks from {pdfs_file}...")
        with open(pdfs_file, 'r', encoding='utf-8') as f:
            pdf_chunks = json.load(f)
        
        for item in pdf_chunks:
            all_documents.append(item['text'])
            all_metadatas.append(item['metadata'])
            all_ids.append(item['id'])
        
        print(f"✅ Loaded {len(pdf_chunks)} PDF chunks")
    else:
        print(f"⚠️  {pdfs_file} not found, skipping PDFs")
    
    if not all_documents:
        print("\n❌ No documents found to embed!")
        print("   Please run:")
        print("   - python scripts/process_exercises.py")
        print("   - python scripts/process_pdfs.py")
        return
    
    print(f"\n📊 Total documents to embed: {len(all_documents)}")
    print(f"💰 Cost: $0.00 (100% FREE with Gemini!)")
    
    # Embed all documents
    print(f"\n🚀 Starting embedding process...")
    print(f"⏱️  Estimated time: ~{len(all_documents) // 100 + 1} minutes")
    
    embeddings = embed_texts_batch(all_documents, batch_size=100)
    
    # Store in ChromaDB
    print(f"\n💾 Storing in ChromaDB...")
    
    # Convert list metadata to strings and remove None values (ChromaDB doesn't support them)
    cleaned_metadatas = []
    for metadata in all_metadatas:
        cleaned = {}
        for key, value in metadata.items():
            # Skip None values
            if value is None:
                continue
            # Convert lists to comma-separated strings
            elif isinstance(value, list):
                cleaned[key] = ', '.join(str(v) for v in value) if value else ''
            else:
                cleaned[key] = value
        cleaned_metadatas.append(cleaned)
    
    collection.add(
        documents=all_documents,
        embeddings=embeddings,
        metadatas=cleaned_metadatas,
        ids=all_ids
    )
    
    print(f"\n✅ Successfully embedded and stored {len(all_documents)} documents!")
    print(f"📁 ChromaDB location: data/chroma_db/")
    
    # Test retrieval
    print(f"\n🔍 Testing retrieval...")
    test_query = "exercises for building chest muscles"
    
    test_result = genai.embed_content(
        model="models/text-embedding-004",
        content=test_query,
        task_type="retrieval_query"
    )
    test_embedding = test_result['embedding']
    
    results = collection.query(
        query_embeddings=[test_embedding],
        n_results=3
    )
    
    print(f"\n📋 Test Query: '{test_query}'")
    print(f"   Top 3 Results:")
    for i, (doc, metadata) in enumerate(zip(results['documents'][0], results['metadatas'][0])):
        print(f"\n   {i+1}. {metadata.get('exercise_name') or metadata.get('source')}")
        print(f"      {doc[:150]}...")
    
    print(f"\n" + "=" * 60)
    print(f"🎉 Embedding complete! Your RAG system is ready!")
    print(f"=" * 60)
    print(f"\n📊 Summary:")
    print(f"   - Exercises: {len([m for m in all_metadatas if m.get('type') == 'exercise'])}")
    print(f"   - PDF chunks: {len([m for m in all_metadatas if m.get('type') == 'guideline'])}")
    print(f"   - Total: {len(all_documents)} documents")
    print(f"   - Embedding model: Gemini text-embedding-004 (768 dimensions)")
    print(f"   - Cost: $0.00 (FREE!)")


if __name__ == "__main__":
    embed_and_store()
