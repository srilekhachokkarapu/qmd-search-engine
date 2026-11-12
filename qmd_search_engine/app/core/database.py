
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = BASE_DIR / "data" / "qmd.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def create_tables():
    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                file_name TEXT NOT NULL,
                file_path TEXT NOT NULL UNIQUE,
                collection TEXT,
                author TEXT,
                category TEXT,
                date TEXT,
                word_count INTEGER,
                character_count INTEGER,
                file_hash TEXT
            )
        """)

        # Migration for existing databases
        columns = {
            row[1]
            for row in cursor.execute(
                "PRAGMA table_info(documents)"
            ).fetchall()
        }

        if "file_hash" not in columns:
            cursor.execute("""
                ALTER TABLE documents
                ADD COLUMN file_hash TEXT
            """)

        # Chunks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                heading TEXT,
                heading_level INTEGER,
                heading_path TEXT,
                content TEXT NOT NULL,
                word_count INTEGER,
                chunk_position INTEGER,

                FOREIGN KEY(document_id)
                REFERENCES documents(document_id)
                ON DELETE CASCADE
            )
        """)

        # Embeddings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                chunk_id TEXT PRIMARY KEY,
                embedding BLOB NOT NULL,
                model_name TEXT,
                dimensions INTEGER,

                FOREIGN KEY(chunk_id)
                REFERENCES chunks(chunk_id)
                ON DELETE CASCADE
            )
        """)

        # FTS5 keyword index
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts
            USING fts5(
                chunk_id UNINDEXED,
                document_title,
                collection,
                heading,
                content,
                tokenize='unicode61'
            )
        """)

        connection.commit()
        print("Database tables created/verified successfully.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
