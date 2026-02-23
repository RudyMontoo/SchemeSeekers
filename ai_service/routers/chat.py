"""
FastAPI Chat Router — Yojna Setu
/chat endpoint: accepts user message + optional state/sector filter
returns Hinglish AI response with matched schemes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["chat"])

# Lazy-load the chain (only on first request, avoids startup delay)
_rag_chain = None

def get_chain():
    global _rag_chain
    if _rag_chain is None:
        from ai_service.rag_chain import build_rag_chain
        _rag_chain = build_rag_chain()
    return _rag_chain


# ── Request / Response models ──────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str
    state: Optional[str] = None        # e.g. "Rajasthan", "Maharashtra"
    sector: Optional[str] = None       # e.g. "health", "education"
    language: Optional[str] = "hinglish"  # hinglish | hindi | english

class SchemeMatch(BaseModel):
    name: str
    sector: str
    state: str
    apply_url: str

class ChatResponse(BaseModel):
    reply: str
    language: str
    matched_schemes: list[SchemeMatch]


# ── Helper: extract scheme metadata from ChromaDB result ──────────────────────
def build_filters(state: Optional[str], sector: Optional[str]) -> Optional[dict]:
    """Build ChromaDB where-clause from optional filters."""
    conditions = []
    if state:
        conditions.append({"state": {"$in": [state, "Central"]}})
    if sector:
        conditions.append({"sector": {"$eq": sector}})
    if len(conditions) == 1:
        return conditions[0]
    if len(conditions) > 1:
        return {"$and": conditions}
    return None


# ── Route ──────────────────────────────────────────────────────────────────────
@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        chain = get_chain()

        # Build retrieval filters
        filters = build_filters(req.state, req.sector)

        # Run RAG chain
        reply = chain.invoke({
            "question": req.message,
            "filters": filters,
        })

        # Fetch top matched schemes for structured response
        from ai_service.rag_chain import get_retriever
        retriever = get_retriever(top_k=3)
        raw_context = retriever(req.message, filters)

        # Parse matched scheme metadata (lightweight)
        import chromadb
        from pathlib import Path
        from chromadb.utils import embedding_functions

        chroma_dir = Path(__file__).parent.parent / "chroma_db"
        client = chromadb.PersistentClient(path=str(chroma_dir))
        ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        collection = client.get_collection(
            name="yojna_setu_schemes", embedding_function=ef
        )
        results = collection.query(
            query_texts=[req.message], n_results=3,
            where=filters if filters else None,
        )
        matched = []
        for meta in (results.get("metadatas") or [[]])[0]:
            matched.append(SchemeMatch(
                name=meta.get("name", ""),
                sector=meta.get("sector", ""),
                state=meta.get("state", "Central"),
                apply_url=meta.get("apply_url", ""),
            ))

        return ChatResponse(
            reply=reply,
            language=req.language or "hinglish",
            matched_schemes=matched,
        )

    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ── Health check ───────────────────────────────────────────────────────────────
@router.get("/health")
async def health():
    return {"status": "ok", "service": "rag_chat"}
