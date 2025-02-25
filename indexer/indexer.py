import os
import uuid
import logging
import time
from typing import Dict, List, Any
from pathlib import Path
from qdrant_client.http.models import Filter

# Import directly from their respective modules
from config import Config
from db_store import MinimaStore, IndexingStatus
from loaders.base import LoaderFactory
from chunkers.base import ChunkerFactory
from storage.qdrant import QdrantStore
from embeddings.sentence_transformers import SentenceTransformersEmbeddings
from search import SearchManager

logger = logging.getLogger(__name__)


class Indexer:
    """Main indexer class that orchestrates document processing and search."""
    
    def __init__(self, config=None):
        """Initialize with optional custom configuration."""
        self.config = config if config else Config()
        
        # Initialize providers using dependency injection
        self.embedding_provider = SentenceTransformersEmbeddings(self.config)
        self.storage_provider = QdrantStore(self.config, self.embedding_provider)
        self.loader_factory = LoaderFactory(self.config)
        self.chunker_factory = ChunkerFactory(self.config)
        self.search_manager = SearchManager(
            self.config, 
            self.storage_provider, 
            self.embedding_provider
        )
    
    def index(self, message: Dict[str, any]) -> None:
        """Index a document based on a message."""
        start = time.time()
        path, file_id, last_updated_seconds = message["path"], message["file_id"], message["last_updated_seconds"]
        logger.info(f"Processing file: {path} (ID: {file_id})")
        
        indexing_status: IndexingStatus = MinimaStore.check_needs_indexing(
            fpath=path, 
            last_updated_seconds=last_updated_seconds
        )
        
        if indexing_status != IndexingStatus.no_need_reindexing:
            logger.info(f"Indexing needed for {path} with status: {indexing_status}")
            try:
                if indexing_status == IndexingStatus.need_reindexing:
                    logger.info(f"Removing {path} from index storage for reindexing")
                    self.remove_from_storage(files_to_remove=[path])
                
                # Get appropriate loader and chunker for this file type
                loader = self.loader_factory.get_loader(path)
                chunker = self.chunker_factory.get_chunker(path)
                
                # Load and split the document
                documents = loader.load()
                chunks = chunker.split_documents(documents)
                
                if not chunks:
                    logger.warning(f"No chunks generated from {path}")
                    return
                
                # Add metadata to chunks
                for doc in chunks:
                    doc.metadata['file_path'] = path
                
                # Generate UUID for each chunk and index them
                uuids = [str(uuid.uuid4()) for _ in range(len(chunks))]
                ids = self.storage_provider.add_documents(documents=chunks, ids=uuids)
                logger.info(f"Successfully indexed {path} with {len(ids)} chunks")
                
            except Exception as e:
                logger.error(f"Failed to index file {path}: {str(e)}")
        else:
            logger.info(f"Skipping {path}, no indexing required. Timestamp didn't change")
        
        end = time.time()
        logger.info(f"Processing took {end - start} seconds for file {path}")
    
    def purge(self, message: Dict[str, any]) -> None:
        """Purge files that no longer exist from the index."""
        existing_file_paths: list[str] = message["existing_file_paths"]
        files_to_remove = MinimaStore.find_removed_files(existing_file_paths=set(existing_file_paths))
        
        if len(files_to_remove) > 0:
            logger.info(f"Purge processing removing old files: {files_to_remove}")
            self.remove_from_storage(files_to_remove)
        else:
            logger.info("Nothing to purge")
    
    def remove_from_storage(self, files_to_remove: list[str]):
        """Remove files from the vector store."""
        filter_condition = self.storage_provider.create_filter_for_paths(files_to_remove)
        self.storage_provider.delete(filter_condition)
        logger.info(f"Removed {len(files_to_remove)} files from storage")
    
    def find(self, query: str) -> Dict[str, any]:
        """Search for documents matching the query."""
        return self.search_manager.search(query)
    
    def embed(self, query: str) -> List[float]:
        """Create embeddings for a query string."""
        return self.embedding_provider.embed_query(query)
