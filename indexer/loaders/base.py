from abc import ABC, abstractmethod
from typing import List, Dict, Type
from pathlib import Path
from langchain.schema import Document

from config import Config


class BaseLoader(ABC):
    """Abstract base class for document loaders."""
    
    def __init__(self, file_path: str):
        """Initialize with file path."""
        self.file_path = file_path
    
    @abstractmethod
    def load(self) -> List[Document]:
        """Load document from file path and return a list of Document objects."""
        pass
    
    def load_and_split(self, text_splitter):
        """Load documents and split them into chunks."""
        documents = self.load()
        return text_splitter.split_documents(documents)


class LoaderFactory:
    """Factory for creating document loaders based on file extension."""
    
    def __init__(self, config: Config):
        """Initialize with configuration."""
        self.config = config
        self._loaders = {}
        
        # Register loaders dynamically to avoid circular imports
        from .markdown import MinimaTextLoader
        from .pdf import PDFLoader 
        from .text import TextLoader
        from .docx import DocxLoader
        from .excel import ExcelLoader
        from .csv import CSVLoader
        from .powerpoint import PowerPointLoader
        
        self._loaders = {
            ".pdf": PDFLoader,
            ".pptx": PowerPointLoader,
            ".ppt": PowerPointLoader, 
            ".xls": ExcelLoader,
            ".xlsx": ExcelLoader,
            ".docx": DocxLoader,
            ".doc": DocxLoader,
            ".txt": TextLoader,
            ".md": MinimaTextLoader,
            ".csv": CSVLoader,
        }
    
    def get_loader(self, file_path: str) -> BaseLoader:
        """Get appropriate loader for the file type."""
        ext = Path(file_path).suffix.lower()
        loader_class = self._loaders.get(ext)
        
        if not loader_class:
            raise ValueError(f"Unsupported file type: {ext}")
            
        return loader_class(file_path)
