from langchain.text_splitter import RecursiveCharacterTextSplitter
from .base import BaseChunker


class MarkdownAwareChunker(BaseChunker):
    """Markdown-specific chunking that respects headers and document structure."""
    
    def create_splitter(self) -> RecursiveCharacterTextSplitter:
        """Create a recursive character text splitter optimized for Markdown."""
        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n## ", "\n### ", "\n#### ", "\n##### ", "\n###### ", "\n\n", "\n", ". ", " ", ""]
        )
