"""
Analytics Router — Yojna Setu AI Hub
Proxies analytics queries to Spring Boot → Supabase.
SQLite has been removed; Supabase is the single source of truth.
"""
import os
import logging
import httpx
from fastapi import APIRouter

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["Analytics"])
SPRING_URL = os.getenv("SPRING_BACKEND_URL", "http://localhost:8080")


@router.get("/popular-schemes")
async def get_popular_schemes(limit: int = 5):
    """Returns the most frequently checked schemes from Supabase."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"{SPRING_URL}/api/internal/status/analytics/popular",
                params={"limit": limit}
            )
            if resp.status_code == 200:
                return resp.json()
    except Exception as e:
        logger.warning(f"Analytics fetch failed: {e}")
    return []


@router.get("/user-states")
async def get_user_states():
    """Placeholder — state analytics available via Spring Boot dashboard."""
    return {"message": "Use Spring Boot /api/internal/status/analytics for full analytics"}


@router.get("/daily-activity")
async def get_daily_activity(limit: int = 7):
    """Placeholder — daily analytics available via Supabase directly."""
    return {"message": "Use Supabase dashboard or Spring Boot analytics endpoints"}
