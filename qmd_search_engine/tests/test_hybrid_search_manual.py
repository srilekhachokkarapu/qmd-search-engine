
from app.core.database import get_connection
from app.search.hybrid_search import HybridSearch


def main():

    connection = get_connection()

    try:
        search_engine = HybridSearch(connection)

        query = "How does supervised learning work?"

        results = search_engine.search(
            query=query,
            top_k=5
        )

        print("\nUSER QUERY:", query)
        print("\nHYBRID SEARCH RESULTS:")

        if not results:
            print("No matching documents found.")
            return

        for index, result in enumerate(results, start=1):

            print("\nResult:", index)
            print("Chunk ID:", result["chunk_id"])
            print("Document:", result["document_title"])
            print("Collection:", result["collection"])
            print("Heading:", result["heading"])

            print("Keyword Rank:", result["keyword_rank"])
            print("Semantic Rank:", result["semantic_rank"])

            print("BM25 Score:", result["bm25_score"])
            print("Similarity Score:", result["similarity_score"])

            print(
                "Hybrid Score:",
                round(result["hybrid_score"], 6)
            )

            print("Content:", result["content"][:300])

    finally:
        connection.close()


if __name__ == "__main__":
    main()
