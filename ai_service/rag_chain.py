"""
RAG Chain — Yojna Setu
LangChain retrieval chain using ChromaDB + Google Gemini

Can be used standalone or imported into FastAPI routers.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from ai_service directory (works regardless of cwd)
_env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_env_path, override=True)

import chromadb
from chromadb.utils import embedding_functions

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# ── Config ────────────────────────────────────────────────────────────────────
CHROMA_DIR = Path(__file__).parent / "chroma_db"
COLLECTION  = "yojna_setu_schemes"
EMBED_MODEL = "all-MiniLM-L6-v2"
TOP_K       = 5           # how many schemes to retrieve per query
GEMINI_MODEL = "gemini-2.0-flash-lite"

# ── System Prompt ─────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """
You are Yojna Sathi — a friendly, empathetic AI assistant of Yojna Setu that helps Indian citizens 
discover and apply for government schemes in simple Hinglish (Hindi + English mix).

Use the retrieved scheme context below to answer the user's question.
Always reply in simple, conversational Hinglish that a village resident would understand.

RULES:
- Only recommend schemes from the retrieved context. Never hallucinate scheme names or amounts.
- For each relevant scheme, mention: Name, Benefit, Who is eligible, and where to apply.
- If the user gives their state, prioritize state-specific schemes.
- If no scheme matches, say so honestly and suggest they visit https://myscheme.gov.in
- Keep response concise — max 3-4 schemes unless more are asked.
- Format benefit amounts in ₹ (Rupee symbol).
- End with an encouraging line.

Retrieved Schemes Context:
{context}
"""

USER_PROMPT = "{question}"

# ── Build retriever from ChromaDB ─────────────────────────────────────────────
def get_retriever(top_k: int = TOP_K):
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL
    )
    collection = client.get_collection(name=COLLECTION, embedding_function=ef)

    def retrieve(query: str, filters: dict = None) -> str:
        where = filters if filters else None
        results = collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where,
        )
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        if not docs:
            return "No matching schemes found."
        chunks = []
        for i, (doc, meta) in enumerate(zip(docs, metas), 1):
            chunks.append(f"[Scheme {i} — {meta.get('state','Central')} / {meta.get('sector','')}]\n{doc}")
        return "\n\n".join(chunks)

    return retrieve


# ── Build the full RAG chain ──────────────────────────────────────────────────
def build_rag_chain():
    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=0.3,
    )
    retriever = get_retriever()

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", USER_PROMPT),
    ])

    chain = (
        {
            "context": lambda x: retriever(x["question"], x.get("filters")),
            "question": RunnablePassthrough() | (lambda x: x["question"]),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


# ── Standalone test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("🔗 Building RAG chain...")
    chain = build_rag_chain()

    test_queries = [
        {"question": "Main ek kisan hoon Rajasthan se, mujhe koi subsidy milegi?"},
        {"question": "Meri beti ke liye koi scholarship hai?"},
        {"question": "Ex-serviceman hun, health insurance milega?"},
        {"question": "Ghar banane ke liye government se paisa milega?"},
    ]

    for q in test_queries:
        print(f"\n❓ {q['question']}")
        print("─" * 60)
        answer = chain.invoke(q)
        print(answer)
        print("═" * 60)
