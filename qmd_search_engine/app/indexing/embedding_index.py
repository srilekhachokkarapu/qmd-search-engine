
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingIndexer:
    """
    Generates vector embeddings for document chunks
    and stores them in the SQLite embeddings table.
    """

    def __init__(
        self,
        connection,
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    ):
        self.connection = connection
        self.model_name = model_name

        # Load the embedding model
        self.model = SentenceTransformer(self.model_name)

    def generate_embedding(self, text):
        """
        Convert text into a normalized numerical vector.
        """

        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        return embedding.astype(np.float32)

    def index_chunk(self, chunk):
        """
        Generate and store the embedding for one chunk.
        """

        embedding = self.generate_embedding(chunk["content"])

        # Convert NumPy vector into bytes for SQLite storage
        embedding_bytes = embedding.tobytes()

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO embeddings (
                chunk_id,
                embedding,
                model_name,
                dimensions
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                chunk["chunk_id"],
                embedding_bytes,
                self.model_name,
                len(embedding)
            )
        )

    def index_chunks(self, chunks, commit=True):
        """
        Generate and store embeddings for multiple chunks.

        commit=True:
            Commit changes immediately.

        commit=False:
            Allow IndexManager to control the transaction.
        """

        if not chunks:
            return

        for chunk in chunks:
            self.index_chunk(chunk)

        if commit:
            self.connection.commit()

    def decode_embedding(self, embedding_bytes):
        """
        Convert stored SQLite bytes back into a NumPy vector.
        """

        return np.frombuffer(
            embedding_bytes,
            dtype=np.float32
        )
