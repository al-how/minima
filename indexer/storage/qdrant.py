from typing import List, Dict, Any, Optional
import logging
from langchain.schema import Document
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from qdrant_client.http.models import Distance, VectorParams, Filter, FieldCondition, MatchValue

from .base import BaseVectorStore
from config import Config
from embeddings.base import BaseEmbeddings

logger = logging.getLogger(__name__)


class QdrantStore(BaseVectorStore):
    """Implementation of vector store using Qdrant."""
    
    def __init__(self, config: Config, embedding_provider: BaseEmbeddings):
        """Initialize with configuration and embedding provider."""
        self.config = config
        self.embedding_provider = embedding_provider
        self.qdrant = self._initialize_qdrant()
        self.vector_store = self._setup_collection()
    
    def _initialize_qdrant(self) -> QdrantClient:
        """Initialize Qdrant client."""
        return QdrantClient(
            host=self.config.QDRANT_BOOTSTRAP,
            port=self.config.QDRANT_PORT
        )
    
    def _setup_collection(self) -> QdrantVectorStore:
        """Set up Qdrant collection."""
        if not self.qdrant.collection_exists(self.config.QDRANT_COLLECTION):
            self.qdrant.create_collection(
                collection_name=self.config.QDRANT_COLLECTION,
                vectors_config=VectorParams(
                    size=self.config.EMBEDDING_SIZE,
                    distance=Distance.COSINE
                ),
            )
        self.qdrant.create_payload_index(
            collection_name=self.config.QDRANT_COLLECTION,
            field_name="fpath",
            field_schema="keyword"
        )
        return QdrantVectorStore(
            client=self.qdrant,
            collection_name=self.config.QDRANT_COLLECTION,
            embedding=self.embedding_provider.get_embeddings(),
        )
    
    def add_documents(self, documents: List[Document], ids: List[str] = None) -> List[str]:
        """Add documents to the vector store."""
        return self.vector_store.add_documents(documents=documents, ids=ids)
    
    def delete(self, filter_condition: Filter) -> None:
        """Delete documents from the vector store based on filter."""
        response = self.qdrant.delete(
            collection_name=self.config.QDRANT_COLLECTION,
            points_selector=filter_condition,
            wait=True
        )
        logger.info(f"Delete response: {response}")
    
    def search(self, query: str, search_type: str = "similarity", **kwargs) -> List[Document]:
        """Search for similar documents in the vector store."""
        return self.vector_store.search(query, search_type=search_type, **kwargs)
    
    def create_filter_for_paths(self, paths: List[str]) -> Filter:
        """Create a filter for matching file paths."""
        return Filter(
            must=[
                FieldCondition(
                    key="fpath",
                    match=MatchValue(value=fpath)
                )
                for fpath in paths
            ]
        )
