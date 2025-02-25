from langchain.text_splitter import RecursiveCharacterTextSplitter
from .base import BaseChunker


class DefaultChunker(BaseChunker):
    """Default chunking strategy with standard separators."""
    
    def create_splitter(self) -> RecursiveCharacterTextSplitter:
        """Create a recursive character text splitter with default separators."""
        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", "! ", "? ", ";", ",", " ", ""]
        )
