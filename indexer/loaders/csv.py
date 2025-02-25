from langchain_community.document_loaders import CSVLoader as LangchainCSVLoader
from .base import BaseLoader


class CSVLoader(LangchainCSVLoader, BaseLoader):
    """CSV file loader."""
    
    def __init__(self, file_path: str, **kwargs):
        LangchainCSVLoader.__init__(self, file_path, **kwargs)
