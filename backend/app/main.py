from fastapi import FastAPI

from app.api.v1 import auth, time_entries, reports
from app.db import base  # noqa: F401


def create_app() -> FastAPI:
    app = FastAPI(title="Team Productivity Tracker API", version="0.1.0")

    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "ok"}

    app.include_router(auth.router, prefix="/api/v1")
    app.include_router(time_entries.router, prefix="/api/v1")
    app.include_router(reports.router, prefix="/api/v1")

    return app


app = create_app()
