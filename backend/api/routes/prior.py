from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from backend.services.config import load_settings

router = APIRouter(prefix="/prior", tags=["prior"])

_VALID_SOURCES = {"fifa", "elo", "odds", "flat"}


def get_manager():
    from backend.api.app import app
    return app.state.manager


class PriorSourcesRequest(BaseModel):
    sources: List[str]


@router.get("/sources")
async def list_sources():
    return load_settings()["prior"]["available_sources"]


@router.get("/active")
async def get_active_sources():
    return {"sources": get_manager().get_prior_sources()}


@router.put("/active")
async def set_active_sources(body: PriorSourcesRequest):
    invalid = set(body.sources) - _VALID_SOURCES
    if invalid:
        raise HTTPException(400, f"Unknown sources: {invalid}")
    if not body.sources:
        raise HTTPException(400, "At least one source required")
    await get_manager().set_prior_sources(body.sources)
    return {"sources": body.sources}
