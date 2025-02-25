from langchain_community.document_loaders import UnstructuredExcelLoader
from .base import BaseLoader


class ExcelLoader(UnstructuredExcelLoader, BaseLoader):
    """Excel spreadsheet loader."""
    
    def __init__(self, file_path: str):
        UnstructuredExcelLoader.__init__(self, file_path)
