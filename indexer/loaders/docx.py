from langchain_community.document_loaders import Docx2txtLoader
from .base import BaseLoader


class DocxLoader(Docx2txtLoader, BaseLoader):
    """Microsoft Word document loader."""
    
    def __init__(self, file_path: str):
        Docx2txtLoader.__init__(self, file_path)
