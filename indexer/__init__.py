# This is needed for Docker compatibility
# Make the Indexer and related classes available at the package level
from indexer import Indexer  # This looks circular but works in Python
from db_store import MinimaStore, IndexingStatus
from factory import create_indexer
from config import Config

__all__ = [
    'Indexer',
    'MinimaStore',
    'IndexingStatus',
    'create_indexer',
    'Config',
]
