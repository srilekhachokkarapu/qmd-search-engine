
import numpy as np
from sentence_transformers import SentenceTransformer


class SemanticSearch:

    def __init__(
        self,
        connection,
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    ):
        self.connection = connection
        self.model_name = model_name

        # Load the same model used during indexing
        self.model = SentenceTransformer(model_name)

        print("Semantic search model loaded successfully.")

    def generate_query_embedding(self, query):
        """
        Convert the user's query into a normalized vector.
        """

        embedding = self.model.encode(
            query,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding.astype(np.float32)

    def search(self, query, top_k=5, collection=None):
        """
        Find chunks using cosine similarity.
        """

        if top_k < 1:
            raise ValueError("top_k must be greater than 0")

        if not query or not query.strip():
            return []

        # Generate embedding for the query
        query_embedding = self.generate_query_embedding(query)

        # Retrieve stored embeddings and their related content
        sql = """
            SELECT
                e.chunk_id,
                e.embedding,
                e.dimensions,
                d.title,
                d.collection,
                c.heading,
                c.heading_path,
                c.content,
                d.document_id
                

            FROM embeddings e

            JOIN chunks c
                ON e.chunk_id = c.chunk_id

            JOIN documents d
                ON c.document_id = d.document_id
        """

        parameters = []

        if collection:
            sql += " WHERE d.collection = ?"
            parameters.append(collection)

        cursor = self.connection.cursor()
        cursor.execute(sql, parameters)

        rows = cursor.fetchall()

        results = []

        for row in rows:

            stored_embedding = np.frombuffer(
                row[1],
                dtype=np.float32
            )

            dimensions = row[2]

            if len(stored_embedding) != dimensions:
                continue

            if len(stored_embedding) != len(query_embedding):
                continue

            # Cosine similarity for normalized vectors
            similarity = float(
                np.dot(query_embedding, stored_embedding)
            )

            results.append({
            "chunk_id": row[0],
            "document_title": row[3],
            "collection": row[4],
            "heading": row[5],
            "heading_path": row[6],
            "content": row[7],
            "document_id": row[8],
            "similarity_score": similarity
        })

        # Highest similarity score comes first
        results.sort(
            key=lambda item: item["similarity_score"],
            reverse=True
        )

        return results[:top_k]
