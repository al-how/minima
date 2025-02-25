"""Central imports module to avoid circular dependencies."""

# This file serves as a central hub for imports 
# to prevent circular dependencies

# Import fundamental modules first
from config import Config
from db_store import MinimaStore, IndexingStatus

# Import storage modules
from storage.base import BaseVectorStore
from storage.qdrant import QdrantStore

# Import embedding modules
from embeddings.base import BaseEmbeddings
from embeddings.sentence_transformers import SentenceTransformersEmbeddings

# Import chunker modules
from chunkers.base import BaseChunker, ChunkerFactory
from chunkers.default import DefaultChunker
from chunkers.markdown_aware import MarkdownAwareChunker
from chunkers.sentence_aware import SentenceAwareChunker
from chunkers.data_aware import DataAwareChunker

# Import loader modules
from loaders.base import BaseLoader, LoaderFactory
from loaders.markdown import MinimaTextLoader
from loaders.pdf import PDFLoader
from loaders.text import TextLoader
from loaders.docx import DocxLoader
from loaders.excel import ExcelLoader
from loaders.csv import CSVLoader
from loaders.powerpoint import PowerPointLoader

# Import search
from search import SearchManager

# Finally, import the main Indexer class
# (this should be imported by other modules from here)
from indexer import Indexer

__all__ = [
    # Config
    'Config',
    
    # Database
    'MinimaStore',
    'IndexingStatus',
    
    # Storage
    'BaseVectorStore',
    'QdrantStore',
    
    # Embeddings
    'BaseEmbeddings',
    'SentenceTransformersEmbeddings',
    
    # Chunkers
    'BaseChunker',
    'ChunkerFactory',
    'DefaultChunker',
    'MarkdownAwareChunker',
    'SentenceAwareChunker',
    'DataAwareChunker',
    
    # Loaders
    'BaseLoader',
    'LoaderFactory',
    'MinimaTextLoader',
    'PDFLoader',
    'TextLoader',
    'DocxLoader',
    'ExcelLoader',
    'CSVLoader',
    'PowerPointLoader',
    
    # Search
    'SearchManager',
    
    # Main class
    'Indexer',
]
