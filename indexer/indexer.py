import os
import uuid
import torch
import logging
import time
from datetime import datetime
import yaml
from dataclasses import dataclass
from typing import List, Dict
from pathlib import Path

from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client.http.models import Distance, VectorParams, Filter, FieldCondition, MatchValue
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.text import TextLoader
from langchain.schema import Document

from langchain_community.document_loaders import (
    TextLoader,
    CSVLoader,
    Docx2txtLoader,
    UnstructuredExcelLoader,
    PyMuPDFLoader,
    UnstructuredPowerPointLoader,
)

from storage import MinimaStore, IndexingStatus

logger = logging.getLogger(__name__)


class MinimaTextLoader(TextLoader):
    """Custom loader for Markdown files that extracts YAML frontmatter."""
    
    def __init__(self, file_path: str, **kwargs):
        super().__init__(file_path, **kwargs)
    
    def _parse_frontmatter(self, content: str) -> tuple[dict, str]:
        """Extract and parse YAML frontmatter from content."""
        if not content.startswith('---\n'):
            return {}, content
            
        # Find the end of frontmatter
        parts = content.split('---\n', 2)
        if len(parts) < 3:
            return {}, content
            
        try:
            frontmatter = yaml.safe_load(parts[1])
            if not isinstance(frontmatter, dict):
                return {}, content
                
            # Clean metadata dictionary
            cleaned_frontmatter = {}
            
            # Handle dates specially
            for key in ['created', 'updated']:
                if key in frontmatter and frontmatter[key]:
                    try:
                        dt = datetime.fromisoformat(str(frontmatter[key]).replace(' ', 'T'))
                        cleaned_frontmatter[key] = dt.isoformat()
                    except ValueError:
                        pass
            
            # Handle all other fields
            for key, value in frontmatter.items():
                if key not in ['created', 'updated']:  # Skip dates as we handled them above
                    if value not in [None, '', [], {}]:  # Skip empty/null values
                        cleaned_frontmatter[key] = value
            
            return cleaned_frontmatter, parts[2]
        except yaml.YAMLError:
            return {}, content
    
    def load(self) -> List[Document]:
        """Load and process the file."""
        with open(self.file_path, encoding=self.encoding) as f:
            content = f.read()
        
        if self.file_path.endswith('.md'):
            metadata, content = self._parse_frontmatter(content)
        else:
            metadata = {}
            
        metadata['file_path'] = self.file_path
        
        return [Document(page_content=content, metadata=metadata)]

@dataclass
class Config:
    EXTENSIONS_TO_LOADERS = {
        ".pdf": PyMuPDFLoader,
        ".pptx": UnstructuredPowerPointLoader,
        ".ppt": UnstructuredPowerPointLoader,
        ".xls": UnstructuredExcelLoader,
        ".xlsx": UnstructuredExcelLoader,
        ".docx": Docx2txtLoader,
        ".doc": Docx2txtLoader,
        ".txt": TextLoader,
        ".md": MinimaTextLoader,
        ".csv": CSVLoader,
    }
    
    DEVICE = torch.device(
        "mps" if torch.backends.mps.is_available() else
        "cuda" if torch.cuda.is_available() else
        "cpu"
    )
    
    START_INDEXING = os.environ.get("START_INDEXING")
    LOCAL_FILES_PATH = os.environ.get("LOCAL_FILES_PATH")
    CONTAINER_PATH = os.environ.get("CONTAINER_PATH")
    QDRANT_COLLECTION = os.environ.get("REMOTE_QDRANT_COLLECTION", "mnm_storage")
    QDRANT_BOOTSTRAP = os.environ.get("REMOTE_QDRANT_HOST", "qdrant")
    QDRANT_PORT = int(os.environ.get("REMOTE_QDRANT_PORT", "6333"))
    EMBEDDING_MODEL_ID = os.environ.get("EMBEDDING_MODEL_ID")
    EMBEDDING_SIZE = os.environ.get("EMBEDDING_SIZE")
    
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

class Indexer:
    def __init__(self):
        self.config = Config()
        self.qdrant = self._initialize_qdrant()
        self.embed_model = self._initialize_embeddings()
        self.document_store = self._setup_collection()
        self.text_splitter = self._initialize_text_splitter()

    def _initialize_qdrant(self) -> QdrantClient:
        return QdrantClient(
            host=self.config.QDRANT_BOOTSTRAP,
            port=self.config.QDRANT_PORT
        )

    def _initialize_embeddings(self) -> HuggingFaceEmbeddings:
        return HuggingFaceEmbeddings(
            model_name=self.config.EMBEDDING_MODEL_ID,
            model_kwargs={'device': self.config.DEVICE},
            encode_kwargs={'normalize_embeddings': False}
        )

    def _initialize_text_splitter(self) -> RecursiveCharacterTextSplitter:
        # Default separator hierarchy for RecursiveCharacterTextSplitter
        separators = ["\n\n", "\n", ". ", "! ", "? ", ";", ",", " ", ""]
        
        # Choose chunking strategy based on default configuration
        if self.config.DEFAULT_CHUNK_STRATEGY.lower() == "markdown_aware":
            # Optimized for Markdown - prioritize headers and paragraph breaks
            separators = ["\n## ", "\n### ", "\n#### ", "\n##### ", "\n###### ", "\n\n", "\n", ". ", " ", ""]
        elif self.config.DEFAULT_CHUNK_STRATEGY.lower() == "sentence_aware":
            # Prioritize sentence boundaries
            separators = [". ", "! ", "? ", "\n\n", "\n", "; ", ", ", " ", ""]
        
        return RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP,
            separators=separators
        )

    def _setup_collection(self) -> QdrantVectorStore:
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
            embedding=self.embed_model,
        )

    def _create_loader(self, file_path: str):
        file_extension = Path(file_path).suffix.lower()
        loader_class = self.config.EXTENSIONS_TO_LOADERS.get(file_extension)
        
        if not loader_class:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        return loader_class(file_path=file_path)

    def _get_file_specific_splitter(self, file_path: str) -> RecursiveCharacterTextSplitter:
        """Create a text splitter optimized for a specific file type."""
        file_extension = Path(file_path).suffix.lower()
        chunk_size = self.config.CHUNK_SIZE
        
        # Define default separators
        separators = ["\n\n", "\n", ". ", "! ", "? ", ";", ",", " ", ""]
        
        # If AUTO_CHUNKING is enabled, select strategy based on file type
        if self.config.AUTO_CHUNKING:
            if file_extension == ".md":
                # Markdown-specific strategy
                chunk_size = self.config.MARKDOWN_CHUNK_SIZE
                separators = ["\n## ", "\n### ", "\n#### ", "\n##### ", "\n###### ", "\n\n", "\n", ". ", " ", ""]
                logger.debug(f"Using markdown-aware chunking for {file_path}")
            elif file_extension == ".pdf":
                # PDF-specific strategy
                chunk_size = self.config.PDF_CHUNK_SIZE
                separators = ["\n\n", "\n", ". ", "! ", "? ", ";", ",", " ", ""]
                logger.debug(f"Using PDF-specific chunking for {file_path}")
            elif file_extension in [".doc", ".docx"]:
                # Word document strategy
                chunk_size = self.config.DOC_CHUNK_SIZE
                separators = ["\n\n", "\n", ". ", "! ", "? ", ";", ",", " ", ""]
                logger.debug(f"Using DOC-specific chunking for {file_path}")
            elif file_extension in [".txt"]:
                # Text file strategy - sentence-focused
                separators = [". ", "! ", "? ", "\n\n", "\n", "; ", ", ", " ", ""]
                logger.debug(f"Using sentence-aware chunking for {file_path}")
            elif file_extension in [".csv", ".xls", ".xlsx"]:
                # Data file strategy - keep rows together when possible
                separators = ["\n", ",", ";", "\t", " ", ""]
                logger.debug(f"Using data-aware chunking for {file_path}")
        else:
            # Apply file-specific chunk sizes but use default separators
            if file_extension == ".md":
                chunk_size = self.config.MARKDOWN_CHUNK_SIZE
            elif file_extension == ".pdf":
                chunk_size = self.config.PDF_CHUNK_SIZE
            elif file_extension in [".doc", ".docx"]:
                chunk_size = self.config.DOC_CHUNK_SIZE
                
        return RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=self.config.CHUNK_OVERLAP,
            separators=separators
        )

    def _process_file(self, loader) -> List[str]:
        try:
            # Create a file-specific text splitter with appropriate strategy and size
            text_splitter = self._get_file_specific_splitter(loader.file_path)
                
            documents = loader.load_and_split(text_splitter)
            if not documents:
                logger.warning(f"No documents loaded from {loader.file_path}")
                return []

            for doc in documents:
                doc.metadata['file_path'] = loader.file_path

            uuids = [str(uuid.uuid4()) for _ in range(len(documents))]
            ids = self.document_store.add_documents(documents=documents, ids=uuids)
            
            logger.info(f"Successfully processed {len(ids)} documents from {loader.file_path}")
            return ids
            
        except Exception as e:
            logger.error(f"Error processing file {loader.file_path}: {str(e)}")
            return []

    def index(self, message: Dict[str, any]) -> None:
        start = time.time()
        path, file_id, last_updated_seconds = message["path"], message["file_id"], message["last_updated_seconds"]
        logger.info(f"Processing file: {path} (ID: {file_id})")
        indexing_status: IndexingStatus = MinimaStore.check_needs_indexing(fpath=path, last_updated_seconds=last_updated_seconds)
        if indexing_status != IndexingStatus.no_need_reindexing:
            logger.info(f"Indexing needed for {path} with status: {indexing_status}")
            try:
                if indexing_status == IndexingStatus.need_reindexing:
                    logger.info(f"Removing {path} from index storage for reindexing")
                    self.remove_from_storage(files_to_remove=[path])
                loader = self._create_loader(path)
                ids = self._process_file(loader)
                if ids:
                    logger.info(f"Successfully indexed {path} with IDs: {ids}")
            except Exception as e:
                logger.error(f"Failed to index file {path}: {str(e)}")
        else:
            logger.info(f"Skipping {path}, no indexing required. timestamp didn't change")
        end = time.time()
        logger.info(f"Processing took {end - start} seconds for file {path}")

    def purge(self, message: Dict[str, any]) -> None:
        existing_file_paths: list[str] = message["existing_file_paths"]
        files_to_remove = MinimaStore.find_removed_files(existing_file_paths=set(existing_file_paths))
        if len(files_to_remove) > 0:
            logger.info(f"purge processing removing old files {files_to_remove}")
            self.remove_from_storage(files_to_remove)
        else:
            logger.info("Nothing to purge")

    def remove_from_storage(self, files_to_remove: list[str]):
        filter_conditions = Filter(
            must=[
                FieldCondition(
                    key="fpath",
                    match=MatchValue(value=fpath)
                )
                for fpath in files_to_remove
            ]
        )
        response = self.qdrant.delete(
            collection_name=self.config.QDRANT_COLLECTION,
            points_selector=filter_conditions,
            wait=True
        )
        logger.info(f"Delete response for {len(files_to_remove)} for files: {files_to_remove} is: {response}")

    def find(self, query: str) -> Dict[str, any]:
        try:
            logger.info(f"Searching for: {query}")
            found = self.document_store.search(query, search_type="similarity")
            
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

    def embed(self, query: str):
        return self.embed_model.embed_query(query)