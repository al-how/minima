from abc import ABC, abstractmethod
from typing import List
from pathlib import Path
from langchain.text_splitter import TextSplitter
from langchain.schema import Document

from config import Config


class BaseChunker(ABC):
    """Abstract base class for text chunking strategies."""
    
    def __init__(self, chunk_size: int, chunk_overlap: int):
        """Initialize with chunk size and overlap."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    @abstractmethod
    def create_splitter(self) -> TextSplitter:
        """Create and return a text splitter implementation."""
        pass
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """Split a list of documents into chunks."""
        splitter = self.create_splitter()
        return splitter.split_documents(documents)


class ChunkerFactory:
    """Factory for creating chunkers based on file type and strategy."""
    
    def __init__(self, config: Config):
        """Initialize with configuration."""
        self.config = config
    
    def get_chunker(self, file_path: str) -> BaseChunker:
        """Get appropriate chunker for the file."""
        ext = Path(file_path).suffix.lower()
        chunk_size = self.config.get_chunk_size(ext)
        
        # If auto chunking is disabled, use the default strategy
        if not self.config.AUTO_CHUNKING:
            strategy = self.config.DEFAULT_CHUNK_STRATEGY.lower()
            return self._create_chunker_by_strategy(strategy, chunk_size)
        
        # Otherwise, select strategy based on file type
        if ext == ".md":
            from .markdown_aware import MarkdownAwareChunker
            return MarkdownAwareChunker(chunk_size, self.config.CHUNK_OVERLAP)
        elif ext == ".pdf":
            from .default import DefaultChunker
            return DefaultChunker(chunk_size, self.config.CHUNK_OVERLAP)
        elif ext in [".doc", ".docx"]:
            from .default import DefaultChunker
            return DefaultChunker(chunk_size, self.config.CHUNK_OVERLAP)
        elif ext == ".txt":
            from .sentence_aware import SentenceAwareChunker
            return SentenceAwareChunker(chunk_size, self.config.CHUNK_OVERLAP)
        elif ext in [".csv", ".xls", ".xlsx"]:
            from .data_aware import DataAwareChunker
            return DataAwareChunker(chunk_size, self.config.CHUNK_OVERLAP)
        else:
            from .default import DefaultChunker
            return DefaultChunker(chunk_size, self.config.CHUNK_OVERLAP)
    
    def _create_chunker_by_strategy(self, strategy: str, chunk_size: int) -> BaseChunker:
        """Create chunker based on named strategy."""
        if strategy == "markdown_aware":
            from .markdown_aware import MarkdownAwareChunker
            return MarkdownAwareChunker(chunk_size, self.config.CHUNK_OVERLAP)
        elif strategy == "sentence_aware":
            from .sentence_aware import SentenceAwareChunker
            return SentenceAwareChunker(chunk_size, self.config.CHUNK_OVERLAP)
        else:  # default
            from .default import DefaultChunker
            return DefaultChunker(chunk_size, self.config.CHUNK_OVERLAP)
