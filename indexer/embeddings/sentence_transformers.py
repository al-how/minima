from typing import List, Any
from langchain_huggingface import HuggingFaceEmbeddings

from .base import BaseEmbeddings
from config import Config


class SentenceTransformersEmbeddings(BaseEmbeddings):
    """Implementation of embeddings using Sentence Transformers."""
    
    def __init__(self, config: Config):
        """Initialize with configuration."""
        self.config = config
        self.model = self._initialize_embeddings()
    
    def _initialize_embeddings(self) -> HuggingFaceEmbeddings:
        """Initialize the HuggingFace embeddings model."""
        return HuggingFaceEmbeddings(
            model_name=self.config.EMBEDDING_MODEL_ID,
            model_kwargs={'device': self.config.DEVICE},
            encode_kwargs={'normalize_embeddings': False}
        )
    
    def get_embeddings(self) -> Any:
        """Get the underlying embedding model instance."""
        return self.model
    
    def embed_query(self, query: str) -> List[float]:
        """Create embeddings for a query string."""
        return self.model.embed_query(query)
    
    def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """Create embeddings for a list of documents."""
        return self.model.embed_documents(documents)
