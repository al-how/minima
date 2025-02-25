from abc import ABC, abstractmethod
from typing import List, Any


class BaseEmbeddings(ABC):
    """Abstract base class for embedding models."""
    
    @abstractmethod
    def get_embeddings(self) -> Any:
        """Get the underlying embedding model instance."""
        pass
    
    @abstractmethod
    def embed_query(self, query: str) -> List[float]:
        """Create embeddings for a query string."""
        pass
    
    @abstractmethod
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Create embeddings for a list of documents."""
        pass
