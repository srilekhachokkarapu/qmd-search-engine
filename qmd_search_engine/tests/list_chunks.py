
from app.core.database import get_connection

connection = get_connection()

try:
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            c.chunk_id,
            d.title,
            d.collection,
            c.heading,
            c.content
        FROM chunks c
        JOIN documents d
            ON c.document_id = d.document_id
        ORDER BY d.collection, c.chunk_position
    """)

    rows = cursor.fetchall()

    print(f"\nTotal chunks: {len(rows)}")

    for row in rows:
        print("\n" + "=" * 70)
        print("Chunk ID:", row[0])
        print("Document:", row[1])
        print("Collection:", row[2])
        print("Heading:", row[3])
        print("Content:", row[4])

finally:
    connection.close()
