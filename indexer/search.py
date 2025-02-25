import logging
from typing import Dict, Set, List, Any

from config import Config
from storage.base import BaseVectorStore
from embeddings.base import BaseEmbeddings

logger = logging.getLogger(__name__)


class SearchManager:
    """Manager for search operations."""
    
    def __init__(self, config: Config, storage_provider: BaseVectorStore, 
                 embedding_provider: BaseEmbeddings):
        """Initialize with dependencies."""
        self.config = config
        self.storage_provider = storage_provider
        self.embedding_provider = embedding_provider
    
    def search(self, query: str) -> Dict[str, Any]:
        """Search for documents matching the query."""
        try:
            logger.info(f"Searching for: {query}")
            found = self.storage_provider.search(query, search_type="similarity")
            
            if not found:
                logger.info("No results found")
                return {"links": set(), "output": ""}

            links = set()
            results = []
            
            for item in found:
                path = item.metadata["file_path"].replace(
                    self.config.CONTAINER_PATH,
                    self.config.LOCAL_FILES_PATH
                )
                links.add(f"file://{path}")
                results.append(item.page_content)

            output = {
                "links": links,
                "output": ". ".join(results)
            }
            
            logger.info(f"Found {len(found)} results")
            return output
            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            return {"error": "Unable to find anything for the given query"}
    
    def embed(self, text: str) -> List[float]:
        """Create embeddings for a text string."""
        return self.embedding_provider.embed_query(text)
