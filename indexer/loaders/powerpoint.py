from langchain_community.document_loaders import UnstructuredPowerPointLoader
from .base import BaseLoader


class PowerPointLoader(UnstructuredPowerPointLoader, BaseLoader):
    """PowerPoint presentation loader."""
    
    def __init__(self, file_path: str):
        UnstructuredPowerPointLoader.__init__(self, file_path)
