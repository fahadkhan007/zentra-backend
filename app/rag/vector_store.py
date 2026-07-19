from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from app.core.config import settings

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001",
    google_api_key=settings.GEMINI_API_KEY,
    task_type="retrieval_query",
)

vectorstore = Chroma(
    collection_name="fitness_knowledge",
    embedding_function=embeddings,
    persist_directory="./data/chroma_db",
)

retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 5})

print(f"✅ Vector store loaded: {vectorstore._collection.count()} documents")
