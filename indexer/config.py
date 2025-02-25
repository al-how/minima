import os
import torch
from pathlib import Path

class Config:
    """Configuration manager for the indexer."""
    
    # File extensions mapping
    EXTENSIONS_TO_LOADERS = {
        ".pdf": "PyMuPDFLoader",
        ".pptx": "UnstructuredPowerPointLoader",
        ".ppt": "UnstructuredPowerPointLoader",
        ".xls": "UnstructuredExcelLoader",
        ".xlsx": "UnstructuredExcelLoader",
        ".docx": "Docx2txtLoader",
        ".doc": "Docx2txtLoader",
        ".txt": "TextLoader",
        ".md": "MinimaTextLoader",
        ".csv": "CSVLoader",
    }
    
    # Device configuration
    DEVICE = torch.device(
        "mps" if torch.backends.mps.is_available() else
        "cuda" if torch.cuda.is_available() else
        "cpu"
    )
    
    # Environment variables
    START_INDEXING = os.environ.get("START_INDEXING")
    LOCAL_FILES_PATH = os.environ.get("LOCAL_FILES_PATH")
    CONTAINER_PATH = os.environ.get("CONTAINER_PATH")
    QDRANT_COLLECTION = os.environ.get("REMOTE_QDRANT_COLLECTION", "mnm_storage")
    QDRANT_BOOTSTRAP = os.environ.get("REMOTE_QDRANT_HOST", "qdrant")
    QDRANT_PORT = int(os.environ.get("REMOTE_QDRANT_PORT", "6333"))
    EMBEDDING_MODEL_ID = os.environ.get("EMBEDDING_MODEL_ID")
    EMBEDDING_SIZE = int(os.environ.get("EMBEDDING_SIZE", "768"))
    
    # Chunking configuration
    CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP = int(os.environ.get("CHUNK_OVERLAP", "200"))
    # Whether to use file-specific chunking strategies automatically
    AUTO_CHUNKING = os.environ.get("AUTO_CHUNKING", "true").lower() == "true"
    # Default strategy if AUTO_CHUNKING is disabled
    DEFAULT_CHUNK_STRATEGY = os.environ.get("DEFAULT_CHUNK_STRATEGY", "default")
    # File-specific chunking sizes
    MARKDOWN_CHUNK_SIZE = int(os.environ.get("MARKDOWN_CHUNK_SIZE", str(CHUNK_SIZE)))
    PDF_CHUNK_SIZE = int(os.environ.get("PDF_CHUNK_SIZE", str(CHUNK_SIZE)))
    DOC_CHUNK_SIZE = int(os.environ.get("DOC_CHUNK_SIZE", str(CHUNK_SIZE)))
    
    @classmethod
    def get_chunk_size(cls, file_extension):
        """Get the appropriate chunk size for a file type."""
        if file_extension == ".md":
            return cls.MARKDOWN_CHUNK_SIZE
        elif file_extension == ".pdf":
            return cls.PDF_CHUNK_SIZE
        elif file_extension in [".doc", ".docx"]:
            return cls.DOC_CHUNK_SIZE
        return cls.CHUNK_SIZE
