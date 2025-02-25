from abc import ABC, abstractmethod
from typing import List, Dict, Any
from langchain.schema import Document


class BaseVectorStore(ABC):
    """Abstract base class for vector stores."""
    
    @abstractmethod
    def add_documents(self, documents: List[Document], ids: List[str] = None) -> List[str]:
        """Add documents to the vector store."""
        pass
    
    @abstractmethod
    def delete(self, filter_condition: Any) -> None:
        """Delete documents from the vector store based on filter."""
        pass
    
    @abstractmethod
    def search(self, query: str, search_type: str = "similarity", **kwargs) -> List[Document]:
        """Search for similar documents in the vector store."""
        pass
