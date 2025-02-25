"""Factory module for creating indexer components."""

from config import Config
from indexer import Indexer
from loaders.base import LoaderFactory
from chunkers.base import ChunkerFactory
from embeddings.sentence_transformers import SentenceTransformersEmbeddings
from storage.qdrant import QdrantStore


def create_indexer(custom_config=None):
    """Create an indexer instance with all dependencies initialized."""
    config = custom_config or Config()
    
    # Create all components
    embedding_provider = SentenceTransformersEmbeddings(config)
    storage_provider = QdrantStore(config, embedding_provider)
    loader_factory = LoaderFactory(config)
    chunker_factory = ChunkerFactory(config)
    
    # Create and return the indexer
    return Indexer(config)
