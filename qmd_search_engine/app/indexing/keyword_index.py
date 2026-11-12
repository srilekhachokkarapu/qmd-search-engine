
class KeywordIndexer:
    """
    Indexes document chunks in the SQLite FTS5 full-text search table.
    """

    def __init__(self, connection):
        self.connection = connection

    def index_chunk(self, chunk):
        """
        Insert one document chunk into the FTS5 keyword index.
        """

        cursor = self.connection.cursor()

        cursor.execute(
            """
            INSERT INTO chunks_fts (
                chunk_id,
                document_title,
                collection,
                heading,
                content
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                chunk["chunk_id"],
                chunk["document_title"],
                chunk["collection"],
                chunk["heading"],
                chunk["content"]
            )
        )

    def index_chunks(self, chunks, commit=True):
        """
        Index multiple chunks.

        commit=True:
            Save changes immediately.

        commit=False:
            Leave the transaction open so IndexManager
            can commit keyword and embedding indexes together.
        """

        if not chunks:
            return

        for chunk in chunks:
            self.index_chunk(chunk)

        if commit:
            self.connection.commit()
