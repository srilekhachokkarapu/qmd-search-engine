
import json
import sqlite3

from fastapi import APIRouter, HTTPException, Query

from app.core.database import get_connection


router = APIRouter(tags=["Documents"])


@router.get("/documents")
def list_documents(
    collection: str | None = None,
    limit: int = Query(default=50, ge=1, le=500)
):
    connection = get_connection()
    connection.row_factory = sqlite3.Row

    try:
        sql = """
            SELECT
                d.document_id,
                d.title,
                d.file_name,
                d.collection,
                d.author,
                d.category,
                d.date,
                d.word_count,
                COUNT(c.chunk_id) AS chunk_count
            FROM documents d
            LEFT JOIN chunks c
                ON d.document_id = c.document_id
        """

        parameters = []

        if collection:
            sql += " WHERE d.collection = ?"
            parameters.append(collection)

        sql += """
            GROUP BY d.document_id
            ORDER BY d.title
            LIMIT ?
        """

        parameters.append(limit)

        rows = connection.execute(
            sql, parameters
        ).fetchall()

        documents = [dict(row) for row in rows]

        return {
            "total_results": len(documents),
            "documents": documents
        }

    finally:
        connection.close()


@router.get("/documents/{document_id}")
def get_document(document_id: str):
    connection = get_connection()
    connection.row_factory = sqlite3.Row

    try:
        document = connection.execute(
            """
            SELECT *
            FROM documents
            WHERE document_id = ?
            """,
            (document_id,)
        ).fetchone()

        if document is None:
            raise HTTPException(
                status_code=404,
                detail="Document not found."
            )

        chunk_rows = connection.execute(
            """
            SELECT
                chunk_id,
                heading,
                heading_level,
                heading_path,
                content,
                word_count,
                chunk_position
            FROM chunks
            WHERE document_id = ?
            ORDER BY chunk_id
            """,
            (document_id,)
        ).fetchall()

        chunks = []

        for row in chunk_rows:
            chunk = dict(row)
            chunk["heading_path"] = json.loads(
                chunk["heading_path"] or "[]"
            )
            chunks.append(chunk)

        return {
            "document": dict(document),
            "total_chunks": len(chunks),
            "chunks": chunks
        }

    finally:
        connection.close()


@router.get("/collections")
def list_collections():
    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                d.collection,
                COUNT(DISTINCT d.document_id) AS document_count,
                COUNT(c.chunk_id) AS chunk_count
            FROM documents d
            LEFT JOIN chunks c
                ON d.document_id = c.document_id
            GROUP BY d.collection
            ORDER BY d.collection
            """
        ).fetchall()

        collections = [
            {
                "name": row[0],
                "document_count": row[1],
                "chunk_count": row[2]
            }
            for row in rows
        ]

        return {
            "total_collections": len(collections),
            "collections": collections
        }

    finally:
        connection.close()
