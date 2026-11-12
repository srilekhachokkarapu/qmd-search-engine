
class DocumentChunker:

    def __init__(self, chunk_size=400, overlap=60):

        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")

        if overlap < 0 or overlap >= chunk_size:
            raise ValueError(
                "overlap must be non-negative and smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_document(self, parsed_document):

        metadata = parsed_document["metadata"]
        sections = parsed_document["sections"]

        chunks = []
        chunk_number = 1

        for section in sections:

            content = section["content"]

            if not content.strip():
                continue

            words = content.split()

            start = 0

            while start < len(words):

                end = min(
                    start + self.chunk_size,
                    len(words)
                )

                chunk_words = words[start:end]

                chunk_text = " ".join(chunk_words)

                chunk = {
                    # "chunk_id": f"C{chunk_number:04d}",
                    "chunk_id": f"{metadata['file_name'].replace('.md', '')}_C{chunk_number:04d}",
                    "document_title": metadata["title"],
                    "file_name": metadata["file_name"],
                    "file_path": metadata["file_path"],
                    "collection": metadata["collection"],
                    "category": metadata["category"],
                    "heading": section["heading"],
                    "heading_level": section["heading_level"],
                    "heading_path": section["heading_path"],
                    "content": chunk_text,
                    "word_count": len(chunk_words),
                    "chunk_position": start
                }

                chunks.append(chunk)

                chunk_number += 1

                if end == len(words):
                    break

                start = end - self.overlap

        return chunks
