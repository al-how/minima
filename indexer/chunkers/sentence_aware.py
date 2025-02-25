from langchain.text_splitter import RecursiveCharacterTextSplitter
from .base import BaseChunker


class SentenceAwareChunker(BaseChunker):
    """Sentence-focused chunking that prioritizes keeping sentences intact."""
    
    def create_splitter(self) -> RecursiveCharacterTextSplitter:
        """Create a recursive character text splitter optimized for sentences."""
        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=[". ", "! ", "? ", "\n\n", "\n", "; ", ", ", " ", ""]
        )
