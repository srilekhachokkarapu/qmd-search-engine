
from app.search.keyword_search import KeywordSearch
from app.search.semantic_search import SemanticSearch


class HybridSearch:

    def __init__(self, connection):

        self.keyword_search = KeywordSearch(connection)
        self.semantic_search = SemanticSearch(connection)

        self.rrf_constant = 60

    def search(self, query, top_k=5, collection=None):

        if top_k < 1:
            raise ValueError("top_k must be greater than 0")

        if not query or not query.strip():
            return []

        # Retrieve a larger candidate list from both search methods
        candidate_k = max(top_k * 3, 10)

        keyword_results = self.keyword_search.search(
            query=query,
            top_k=candidate_k,
            collection=collection
        )

        semantic_results = self.semantic_search.search(
            query=query,
            top_k=candidate_k,
            collection=collection
        )

        combined_results = {}

        # Add keyword search rankings
        for rank, result in enumerate(keyword_results, start=1):

            chunk_id = result["chunk_id"]

            combined_results[chunk_id] = {
                "chunk_id": chunk_id,
                "document_id": result["document_id"],
                "document_title": result["document_title"],
                "collection": result["collection"],
                "heading": result["heading"],
                "heading_path": result["heading_path"],
                "content": result["content"],
                "keyword_rank": rank,
                "semantic_rank": None,
                "bm25_score": result["relevance_score"],
                "similarity_score": None,
                "hybrid_score": 1 / (
                    self.rrf_constant + rank
                )
            }

        # Add semantic search rankings
        for rank, result in enumerate(semantic_results, start=1):

            chunk_id = result["chunk_id"]

            semantic_contribution = 1 / (
                self.rrf_constant + rank
            )

            if chunk_id in combined_results:

                combined_results[chunk_id]["semantic_rank"] = rank

                combined_results[chunk_id]["similarity_score"] = (
                    result["similarity_score"]
                )

                combined_results[chunk_id]["hybrid_score"] += (
                    semantic_contribution
                )

            else:

                combined_results[chunk_id] = {
                    "chunk_id": chunk_id,
                     "document_id": result["document_id"],
                    "document_title": result["document_title"],
                    "collection": result["collection"],
                    "heading": result["heading"],
                    "heading_path": result["heading_path"],
                    "content": result["content"],
                    "keyword_rank": None,
                    "semantic_rank": rank,
                    "bm25_score": None,
                    "similarity_score": result["similarity_score"],
                    "hybrid_score": semantic_contribution
                }

        # Sort by combined RRF score
        final_results = sorted(
            combined_results.values(),
            key=lambda item: item["hybrid_score"],
            reverse=True
        )

        return final_results[:top_k]
