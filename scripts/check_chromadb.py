import chromadb

# Check ChromaDB status
client = chromadb.PersistentClient(path='data/chroma_db')

try:
    coll = client.get_collection('fitness_knowledge')
    count = coll.count()
    print(f"✅ Collection 'fitness_knowledge' exists with {count} documents")
    
    if count > 0:
        # Test query
        results = coll.peek(limit=3)
        print(f"\n📋 Sample documents:")
        for i, (doc, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
            print(f"\n{i+1}. {metadata.get('exercise_name') or metadata.get('source')}")
            print(f"   {doc[:100]}...")
    else:
        print("⚠️  Collection is empty")
        
except Exception as e:
    print(f"❌ Collection doesn't exist or error: {e}")
    print("   Need to run embedding script")
