import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Must run before the imports below: agents.auth_service reads JWT_SECRET_KEY
# at module level, so a .env loaded any later would have no effect.
load_dotenv()

from agents.auth_routes import auth_router  # noqa: E402
from agents.routes import (  # noqa: E402
    analytics_router,
    movement_router,
    product_router,
    supplier_router,
)
from db.database import init_db  # noqa: E402

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
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(auth_router)
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
