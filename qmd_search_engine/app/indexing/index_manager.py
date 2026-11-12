
import hashlib
from pathlib import Path

from app.core.database import get_connection, create_tables
from app.ingestion.loader import MarkdownLoader
from app.ingestion.parser import MarkdownParser
from app.ingestion.chunking import DocumentChunker
from app.indexing.keyword_index import KeywordIndexer
from app.indexing.embedding_index import EmbeddingIndexer


class IndexManager:
    """
    Manages document ingestion and incremental indexing.

    Detects:
    1. New documents
    2. Modified documents
    3. Unchanged documents
    4. Deleted documents
    """

    def __init__(self):
        self.loader = MarkdownLoader()
        self.parser = MarkdownParser()
        self.chunker = DocumentChunker(
            chunk_size=400,
            overlap=60
        )

    # --------------------------------------------------
    # Convert values into SQLite-compatible values
    # --------------------------------------------------

    def to_db_text(self, value, default=None):
        """
        Convert lists and other values into SQLite-compatible text.
        """

        if value is None:
            return default

        if isinstance(value, (list, tuple, set)):
            return ", ".join(str(item) for item in value)

        return str(value)

    # --------------------------------------------------
    # Generate document ID
    # --------------------------------------------------

    def generate_document_id(self, file_path):
        normalized_path = str(Path(file_path).resolve())

        return hashlib.sha256(
            normalized_path.encode("utf-8")
        ).hexdigest()

    # --------------------------------------------------
    # Generate file hash
    # --------------------------------------------------

    def generate_file_hash(self, file_path):
        file_content = Path(file_path).read_bytes()

        return hashlib.sha256(file_content).hexdigest()

    # --------------------------------------------------
    # Normalize file path
    # --------------------------------------------------

    def normalize_path(self, file_path):
        return str(Path(file_path).resolve())

    # --------------------------------------------------
    # Delete document and its FTS entries
    # --------------------------------------------------

    def delete_document(self, connection, document_id):

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT chunk_id
            FROM chunks
            WHERE document_id = ?
            """,
            (document_id,)
        )

        chunk_ids = cursor.fetchall()

        for row in chunk_ids:
            cursor.execute(
                """
                DELETE FROM chunks_fts
                WHERE chunk_id = ?
                """,
                (row[0],)
            )

        cursor.execute(
            """
            DELETE FROM documents
            WHERE document_id = ?
            """,
            (document_id,)
        )

    # --------------------------------------------------
    # Insert document and chunks
    # --------------------------------------------------

    def insert_document(
        self,
        connection,
        parsed_document,
        document_id,
        file_hash,
        chunks
    ):

        cursor = connection.cursor()

        metadata = parsed_document["metadata"]

        file_path = self.normalize_path(
            metadata["file_path"]
        )

        file_name = Path(file_path).name

        # Convert collection into a string
        collection = self.to_db_text(
            parsed_document.get("collection")
            or metadata.get("collection")
            or metadata.get("category"),
            default="default"
        )

        # Convert category into a string
        category = self.to_db_text(
            metadata.get("category"),
            default=collection
        )

        # Prepare all database text values
        title = self.to_db_text(
            metadata.get("title"),
            default=file_name
        )

        author = self.to_db_text(
            metadata.get("author"),
            default="Unknown"
        )

        date = self.to_db_text(
            metadata.get("date")
        )

        cursor.execute(
            """
            INSERT INTO documents (
                document_id,
                title,
                file_name,
                file_path,
                collection,
                author,
                category,
                date,
                word_count,
                character_count,
                file_hash
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                document_id,
                title,
                file_name,
                file_path,
                collection,
                author,
                category,
                date,
                int(metadata.get("word_count") or 0),
                int(metadata.get("character_count") or 0),
                file_hash
            )
        )

        # Insert chunks
        for chunk in chunks:

            cursor.execute(
                """
                INSERT INTO chunks (
                    chunk_id,
                    document_id,
                    heading,
                    heading_level,
                    heading_path,
                    content,
                    word_count,
                    chunk_position
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk["chunk_id"],
                    document_id,
                    self.to_db_text(chunk.get("heading")),
                    chunk.get("heading_level"),
                    self.to_db_text(chunk.get("heading_path")),
                    chunk["content"],
                    int(chunk.get("word_count") or 0),
                    int(chunk.get("chunk_position") or 0)
                )
            )

    # --------------------------------------------------
    # Main incremental indexing process
    # --------------------------------------------------

    def run_indexing(self):

        create_tables()

        connection = get_connection()

        try:

            # Load Markdown documents
            documents = self.loader.load_documents()

            print(
                f"\nTotal Markdown documents found: {len(documents)}"
            )

            # Parse documents and generate hashes
            parsed_documents = []

            for document in documents:

                parsed = self.parser.parse(document)

                file_path = self.normalize_path(
                    parsed["metadata"]["file_path"]
                )

                file_hash = self.generate_file_hash(file_path)

                parsed_documents.append({
                    "parsed": parsed,
                    "file_path": file_path,
                    "file_hash": file_hash
                })

            # Retrieve existing database records
            cursor = connection.cursor()

            cursor.execute(
                """
                SELECT document_id, file_path, file_hash
                FROM documents
                """
            )

            existing_rows = cursor.fetchall()

            existing_documents = {}

            for row in existing_rows:

                document_id = row[0]
                file_path = self.normalize_path(row[1])
                file_hash = row[2]

                existing_documents[file_path] = {
                    "document_id": document_id,
                    "file_hash": file_hash
                }

            # Identify new, modified and unchanged documents
            new_documents = []
            modified_documents = []
            unchanged_count = 0

            current_paths = set()

            for item in parsed_documents:

                file_path = item["file_path"]
                file_hash = item["file_hash"]

                current_paths.add(file_path)

                existing = existing_documents.get(file_path)

                if existing is None:

                    new_documents.append(item)

                elif existing["file_hash"] == file_hash:

                    unchanged_count += 1

                else:

                    item["old_document_id"] = (
                        existing["document_id"]
                    )

                    modified_documents.append(item)

            # Identify deleted documents
            deleted_documents = []

            for file_path, existing in existing_documents.items():

                if file_path not in current_paths:

                    deleted_documents.append({
                        "file_path": file_path,
                        "document_id": existing["document_id"]
                    })

            # Prepare chunks for new and modified documents
            documents_to_process = (
                new_documents + modified_documents
            )

            prepared_documents = []
            all_chunks = []

            for item in documents_to_process:

                parsed = item["parsed"]

                chunks = self.chunker.chunk_document(parsed)

                document_id = self.generate_document_id(
                    item["file_path"]
                )

                prepared_documents.append({
                    "parsed": parsed,
                    "file_path": item["file_path"],
                    "file_hash": item["file_hash"],
                    "document_id": document_id,
                    "chunks": chunks
                })

                all_chunks.extend(chunks)

            # Start database transaction
            connection.execute("BEGIN")

            # Delete old versions of modified documents
            for item in modified_documents:

                self.delete_document(
                    connection,
                    item["old_document_id"]
                )

            # Delete removed documents
            for item in deleted_documents:

                self.delete_document(
                    connection,
                    item["document_id"]
                )

            # Insert new and modified documents
            for item in prepared_documents:

                self.insert_document(
                    connection=connection,
                    parsed_document=item["parsed"],
                    document_id=item["document_id"],
                    file_hash=item["file_hash"],
                    chunks=item["chunks"]
                )

            # Update keyword and embedding indexes
            if all_chunks:

                keyword_indexer = KeywordIndexer(connection)

                keyword_indexer.index_chunks(
                    all_chunks,
                    commit=False
                )

                embedding_indexer = EmbeddingIndexer(connection)

                embedding_indexer.index_chunks(
                    all_chunks,
                    commit=False
                )

            # Commit all changes together
            connection.commit()

            # Generate indexing report
            report = {
                "total_documents": len(documents),
                "new_documents": len(new_documents),
                "modified_documents": len(modified_documents),
                "unchanged_documents": unchanged_count,
                "deleted_documents": len(deleted_documents),
                "new_chunks_indexed": len(all_chunks)
            }

            print(
                "\n========== INCREMENTAL INDEXING REPORT =========="
            )

            print(
                f"Total documents found : {report['total_documents']}"
            )
            print(
                f"New documents         : {report['new_documents']}"
            )
            print(
                f"Modified documents    : {report['modified_documents']}"
            )
            print(
                f"Unchanged documents   : {report['unchanged_documents']}"
            )
            print(
                f"Deleted documents     : {report['deleted_documents']}"
            )
            print(
                f"New chunks indexed    : {report['new_chunks_indexed']}"
            )

            print("==================================================")

            return report

        except Exception as error:

            connection.rollback()

            print("\nIndexing failed!")
            print(f"Error: {error}")

            raise

        finally:

            connection.close()


# ------------------------------------------------------
# Run indexing directly from terminal
# ------------------------------------------------------

if __name__ == "__main__":

    index_manager = IndexManager()

    index_manager.run_indexing()
