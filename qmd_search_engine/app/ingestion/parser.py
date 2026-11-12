
import re
from pathlib import Path


class MarkdownParser:

    def parse(self, document):

        content = document["content"]

        # Extract front matter metadata
        metadata, markdown_content = self.extract_metadata(content)

        # Extract sections and headings
        sections = self.extract_sections(markdown_content)

        # Document metadata
        document_info = {
            "file_name": document["file_name"],
            "file_path": document["file_path"],
            "collection": document["collection"],
            "title": metadata.get(
                "title",
                Path(document["file_name"]).stem
            ),
            "author": metadata.get("author", "Unknown"),
            "category": metadata.get(
                "category",
                document["collection"]
            ),
            "date": metadata.get("date", None),
            "word_count": len(markdown_content.split()),
            "character_count": len(markdown_content),
            "headings": [
                section["heading"]
                for section in sections
                if section["heading"]
            ]
        }

        return {
            "metadata": document_info,
            "sections": sections
        }

    def extract_metadata(self, content):

        metadata = {}

        # Check whether YAML front matter exists
        # pattern = r"\A---\s*\n(.*?)\n---\s*(?:\n|$)"
        pattern = r"\A\s*---\s*\n(.*?)\n---\s*(?:\n|$)"

        match = re.match(pattern, content, re.DOTALL)

        if match:

            front_matter = match.group(1)

            for line in front_matter.splitlines():

                if ":" in line:

                    key, value = line.split(":", 1)

                    metadata[key.strip()] = (
                        value.strip().strip("\"'")
                    )

            markdown_content = content[match.end():]

        else:
            markdown_content = content

        return metadata, markdown_content

    def extract_sections(self, content):

        sections = []

        current_section = {
            "heading": "Introduction",
            "heading_level": 0,
            "heading_path": [],
            "content": []
        }

        heading_stack = []

        for line in content.splitlines():

            # Identify Markdown headings
            match = re.match(
                r"^(#{1,6})\s+(.+?)\s*#*\s*$",
                
                line
            )

            if match:

                # Save previous section
                section_text = "\n".join(
                    current_section["content"]
                ).strip()

                if section_text:
                    current_section["content"] = section_text
                    sections.append(current_section)

                level = len(match.group(1))
                heading = match.group(2).strip()

                # Maintain heading hierarchy
                heading_stack = heading_stack[:level - 1]
                heading_stack.append(heading)

                current_section = {
                    "heading": heading,
                    "heading_level": level,
                    "heading_path": heading_stack.copy(),
                    "content": []
                }

            else:
                current_section["content"].append(line)

        # Save the last section
        section_text = "\n".join(
            current_section["content"]
        ).strip()

        if section_text:
            current_section["content"] = section_text
            sections.append(current_section)

        return sections
