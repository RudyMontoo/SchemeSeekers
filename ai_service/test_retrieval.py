"""Quick test: ChromaDB retrieval works without any Gemini key"""
import sys
sys.path.insert(0, "/home/rudra/dev/playground/Yojna_Setu")

import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path

CHROMA_DIR = Path("/home/rudra/dev/playground/Yojna_Setu/ai_service/chroma_db")
COLLECTION  = "yojna_setu_schemes"
EMBED_MODEL = "all-MiniLM-L6-v2"

print("🔍 Connecting to ChromaDB...")
client = chromadb.PersistentClient(path=str(CHROMA_DIR))
ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=EMBED_MODEL)
col = client.get_collection(name=COLLECTION, embedding_function=ef)
print(f"✅ Collection '{COLLECTION}': {col.count()} documents\n")

queries = [
    ("kisan subsidy Rajasthan", {}),
    ("beti padhai scholarship", {}),
    ("ex-serviceman health insurance", {}),
    ("ghar banane paisa milega", {}),
    ("tribal students scholarship", {"sector": {"$eq": "tribal"}}),
]

for query, filters in queries:
    where = filters if filters else None
    results = col.query(query_texts=[query], n_results=3, where=where)
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    print(f"❓ Query: '{query}'")
    for i, (doc, meta) in enumerate(zip(docs, metas), 1):
        first_line = doc.split("\n")[0]
        print(f"  {i}. [{meta['state']} | {meta['sector']}] {first_line}")
    print()
print("✅ ChromaDB retrieval test PASSED")
