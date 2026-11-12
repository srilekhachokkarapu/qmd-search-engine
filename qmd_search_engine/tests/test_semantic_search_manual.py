
from app.core.database import get_connection
from app.search.semantic_search import SemanticSearch


def main():

    connection = get_connection()

    try:
        search_engine = SemanticSearch(connection)

        query = "How does supervised learning work?"

        results = search_engine.search(
            query=query,
            top_k=5
        )

        print("\nUSER QUERY:", query)
        print("\nSEMANTIC SEARCH RESULTS:")

        if not results:
            print("No matching documents found.")
            return

        for index, result in enumerate(results, start=1):

            print("\nResult:", index)
            print("Chunk ID:", result["chunk_id"])
            print("Document:", result["document_title"])
            print("Collection:", result["collection"])
            print("Heading:", result["heading"])
            print(
                "Similarity Score:",
                round(result["similarity_score"], 4)
            )
            print("Content:", result["content"][:300])

    finally:
        connection.close()


if __name__ == "__main__":
    main()
