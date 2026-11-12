
from pathlib import Path


class MarkdownLoader:

    def __init__(self, documents_path="documents"):
        self.documents_path = Path(documents_path)

    def load_documents(self):

        documents = []

        # Check whether folder exists
        if not self.documents_path.exists():
            raise FileNotFoundError(
                f"Documents folder not found: {self.documents_path}"
            )

        # Find all Markdown files recursively
        markdown_files = self.documents_path.rglob("*.md")

        for file_path in markdown_files:

            try:
                content = file_path.read_text(
                    encoding="utf-8"
                )

                document = {
                    "file_name": file_path.name,
                    "file_path": str(file_path.resolve()),
                    "collection": file_path.parent.name,
                    "content": content
                }

                documents.append(document)

            except (OSError, UnicodeDecodeError) as error:
                print(f"Error reading {file_path}: {error}")

        return documents
