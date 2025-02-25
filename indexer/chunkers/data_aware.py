from langchain.text_splitter import RecursiveCharacterTextSplitter
from .base import BaseChunker


class DataAwareChunker(BaseChunker):
    """Data-focused chunking for CSV, Excel, and other structured data files."""
    
    def create_splitter(self) -> RecursiveCharacterTextSplitter:
        """Create a recursive character text splitter optimized for data files."""
        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n", ",", ";", "\t", " ", ""]
        )
