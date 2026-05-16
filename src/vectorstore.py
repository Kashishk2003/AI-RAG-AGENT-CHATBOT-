import json
import os
import chromadb
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv()

CHROMA_PATH = "./data/chroma"
COLLECTION_NAME = "debales"


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    
    # Built-in — no extra install needed
    ef = embedding_functions.DefaultEmbeddingFunction()
    
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef
    )
    return collection

def build_vectorstore():
    print("Loading scraped data...")
    with open("data/scraped.json", "r") as f:
        chunks = json.load(f)

    collection = get_collection()

    print(f"Indexing {len(chunks)} chunks into ChromaDB...")
    
    for i, chunk in enumerate(chunks):
        collection.upsert(
            documents=[chunk["text"]],
            metadatas=[{"source": chunk["source"]}],
            ids=[f"chunk_{i}"]
        )
        if i % 100 == 0:
            print(f"  → {i}/{len(chunks)} done...")

    print(f"✅ Vectorstore built! {len(chunks)} chunks indexed.")

def query_vectorstore(question, n_results=4):
    collection = get_collection()
    results = collection.query(
        query_texts=[question],
        n_results=n_results
    )
    
    docs = results["documents"][0]
    sources = [m["source"] for m in results["metadatas"][0]]
    
    context = "\n\n".join([
        f"[Source: {sources[i]}]\n{docs[i]}" 
        for i in range(len(docs))
    ])
    
    return context

if __name__ == "__main__":
    build_vectorstore()