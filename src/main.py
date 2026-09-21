import logging
import os
import sys
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

from auth.router import router as r_router
from config.alembic import upgrade_all_migrations
from config.settings import settings
from share import router as routers
from users.router import router as u_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="ITS Test API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        swagger_ui_parameters={"persistAuthorization": True},
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )
    app.include_router(r_router, prefix="/api")
    app.include_router(u_router, prefix="/api")
    app.include_router(routers.health_router)

    templates_dir = Path(__file__).parent / "auth" / "templates"
    app.state.templates = Jinja2Templates(directory=str(templates_dir))

    return app


app = create_app()

if __name__ == "__main__":
    upgrade_all_migrations()
    port = int(os.getenv("PORT", str(settings.PORT)))
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=port,
        reload=settings.RELOAD,
        access_log=False,
    )
