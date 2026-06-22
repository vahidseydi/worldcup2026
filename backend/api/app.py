import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.services.config import load_settings
from backend.services.state_manager import StateManager
from backend.services.football_api import FootballAPIClient
from backend.api.routes import tournament, prior, predictions, simulation, admin

logger = logging.getLogger(__name__)

# Absolute path to the built Vue app — works regardless of cwd
_FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    cfg = load_settings()
    app.state.manager = StateManager()
    app.state.api_client = FootballAPIClient()

    async def on_update(matches):
        try:
            await app.state.manager.ingest_api_matches(matches)
        except Exception:
            logger.exception("ingest_api_matches failed")

    poll_task = asyncio.create_task(app.state.api_client.poll(on_update))
    poll_task.add_done_callback(
        lambda t: logger.exception("Poll task died", exc_info=t.exception()) if not t.cancelled() and t.exception() else None
    )
    logger.info("API poller started")

    yield

    poll_task.cancel()
    await app.state.api_client.close()
    logger.info("API poller stopped")


def create_app() -> FastAPI:
    cfg = load_settings()["app"]

    app = FastAPI(
        title=cfg["name"],
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cfg["cors_origins"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(tournament.router, prefix="/api")
    app.include_router(prior.router, prefix="/api")
    app.include_router(predictions.router, prefix="/api")
    app.include_router(simulation.router, prefix="/api")
    app.include_router(admin.router, prefix="/api")

    @app.get("/health")
    async def health():
        return {"status": "ok"}

    # Serve the Vue SPA.  API routes (registered above) always take priority
    # because FastAPI matches them before reaching the catch-all below.
    if _FRONTEND_DIST.exists():
        # Static assets (JS/CSS/images produced by Vite)
        app.mount(
            "/assets",
            StaticFiles(directory=_FRONTEND_DIST / "assets"),
            name="assets",
        )

        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa(full_path: str):
            """Return index.html for every non-API path so Vue Router works."""
            index = _FRONTEND_DIST / "index.html"
            return FileResponse(index)

    return app


app = create_app()
