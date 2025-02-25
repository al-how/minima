from langchain_community.document_loaders import TextLoader as LangchainTextLoader
from .base import BaseLoader


class TextLoader(LangchainTextLoader, BaseLoader):
    """Plain text document loader."""
    
    def __init__(self, file_path: str, **kwargs):
        LangchainTextLoader.__init__(self, file_path, **kwargs)
