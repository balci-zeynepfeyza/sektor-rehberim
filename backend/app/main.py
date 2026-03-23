from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from backend.app.api.comments import router as comments_router
from backend.app.core.config import get_settings
from backend.app.api.interview_questions import router as interview_questions_router
from backend.app.api.qr import router as qr_router
from backend.app.db.local_store import LocalSQLiteCommentStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize storage once on startup for single-process MVP.
    settings = get_settings()
    os.makedirs(settings.app_data_dir, exist_ok=True)
    store = LocalSQLiteCommentStore(sqlite_path=settings.sqlite_path)
    store.init()
    app.state.store = store
    app.state.settings = settings
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="Sektor Rehberim", lifespan=lifespan)

    # API
    app.include_router(comments_router, prefix="/api")
    app.include_router(interview_questions_router, prefix="/api")
    app.include_router(qr_router, prefix="/api")

    # Minimal static hosting (optional for future expansion).
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.isdir(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/", response_class=HTMLResponse)
    async def index() -> HTMLResponse:
        index_path = os.path.join(static_dir, "index.html")
        with open(index_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())

    return app


app = create_app()

