import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from db.database import init_db
from agents.routes import (
    product_router,
    movement_router,
    supplier_router,
    analytics_router,
)

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Inventory Management API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type"],
)

app.include_router(product_router)
app.include_router(movement_router)
app.include_router(supplier_router)
app.include_router(analytics_router)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "Inventory Management API"}


# Serve frontend static files in production (Docker)
if os.path.isdir(STATIC_DIR):
    app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")

    @app.get("/{path:path}")
    def serve_frontend(path: str):
        file_path = os.path.realpath(os.path.join(STATIC_DIR, path))
        if file_path.startswith(os.path.realpath(STATIC_DIR)) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(STATIC_DIR, "index.html"))
