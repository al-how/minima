from langchain_community.document_loaders import PyMuPDFLoader
from .base import BaseLoader


class PDFLoader(PyMuPDFLoader, BaseLoader):
    """PDF document loader."""
    
    def __init__(self, file_path: str):
        PyMuPDFLoader.__init__(self, file_path)
