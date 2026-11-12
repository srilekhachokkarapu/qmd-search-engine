
from typing import Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.database import get_connection
from app.search.keyword_search import KeywordSearch
from app.search.semantic_search import SemanticSearch
from app.search.hybrid_search import HybridSearch


router = APIRouter(
    prefix="/search",
    tags=["Search"]
)


# --------------------------------------------------
# SEARCH REQUEST MODEL
# --------------------------------------------------

class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    mode: Literal["keyword", "semantic", "hybrid"] = "hybrid"
    top_k: int = Field(default=5, ge=1, le=100)
    collection: Optional[str] = None


# --------------------------------------------------
# SEARCH API
# --------------------------------------------------

@router.post("")
def search_documents(request: SearchRequest):

    # Validate empty or whitespace-only queries
    if not request.query.strip():
        raise HTTPException(
            status_code=422,
            detail="Search query cannot be empty."
        )

    connection = get_connection()

    try:

        # Select search engine based on search mode
        if request.mode == "keyword":
            search_engine = KeywordSearch(connection)

        elif request.mode == "semantic":
            search_engine = SemanticSearch(connection)

        else:
            search_engine = HybridSearch(connection)

        # Execute search
        results = search_engine.search(
            query=request.query,
            top_k=request.top_k,
            collection=request.collection
        )

        # Handle empty search results
        if not results:

            if request.collection:
                message = (
                    f"No matching results found in the "
                    f"'{request.collection}' collection. "
                    "Try different keywords or another collection."
                )

            else:
                message = (
                    "No matching results found. "
                    "Try a different search query."
                )

        else:
            message = "Search completed successfully."

        # Return API response
        return {
            "query": request.query,
            "mode": request.mode,
            "collection": request.collection,
            "total_results": len(results),
            "message": message,
            "results": results
        }

    finally:
        # Always close database connection
        connection.close()
