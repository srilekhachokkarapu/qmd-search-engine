
import re


class KeywordSearch:
    def __init__(self, connection):
        self.connection = connection

    def prepare_query(self, query):
        """
        Convert user input into a safe FTS5 query.
        Example:
        supervised learning -> "supervised" OR "learning"
        """
        words = re.findall(r"\w+", query.lower())

        if not words:
            return ""

        # Remove duplicate words while preserving order
        words = list(dict.fromkeys(words))

        # Quote each word to avoid FTS5 syntax errors
        return " OR ".join(f'"{word}"' for word in words)

    def search(self, query, top_k=5, collection=None):
        """
        Search Markdown chunks using SQLite FTS5.
        """

        if top_k < 1:
            raise ValueError("top_k must be greater than 0")

        match_query = self.prepare_query(query)

        if not match_query:
            return []

        sql = """
            SELECT
                c.chunk_id,
                d.title AS document_title,
                d.collection,
                c.heading,
                c.heading_path,
                c.content,
                d.document_id,
                bm25(
                    chunks_fts,
                    0.0,
                    1.0,
                    0.5,
                    2.0,
                    1.0
                ) AS relevance_score

            FROM chunks_fts

            JOIN chunks c
                ON chunks_fts.chunk_id = c.chunk_id

            JOIN documents d
                ON c.document_id = d.document_id

            WHERE chunks_fts MATCH ?
        """

        parameters = [match_query]

        if collection:
            sql += " AND d.collection = ?"
            parameters.append(collection)

        sql += """
            ORDER BY relevance_score ASC
            LIMIT ?
        """

        parameters.append(top_k)

        cursor = self.connection.cursor()
        cursor.execute(sql, parameters)

        rows = cursor.fetchall()

        results = []

        for row in rows:
            results.append({
    "chunk_id": row[0],
    "document_title": row[1],
    "collection": row[2],
    "heading": row[3],
    "heading_path": row[4],
    "content": row[5],
    "document_id": row[6],
    "relevance_score": row[7]
})
        for result in results:
            print("Document:", result["document_title"])
            print("BM25 Relevance Score:", result["relevance_score"])
        return results

        