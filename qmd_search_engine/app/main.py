
from fastapi import FastAPI

from app.api.search_routes import router as search_router
from app.api.document_routes import router as document_router
from pathlib import Path
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse



app = FastAPI(
    title="QMD Search Engine",
    description=(
        "Python-based Markdown document search engine "
        "with keyword, semantic and hybrid search."
    ),
    version="1.0.0"
)


@app.get("/", tags=["System"])
def home():
    return {
        "message": "Welcome to QMD Search Engine",
        "status": "Running successfully"
    }


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy"}


app.include_router(search_router)
app.include_router(document_router)

BASE_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = BASE_DIR / "frontend"

app.mount(
    "/static",
    StaticFiles(directory=str(FRONTEND_DIR)),
    name="static"
)

@app.get("/ui", include_in_schema=False)
def frontend_home():
    return FileResponse(FRONTEND_DIR / "index.html")