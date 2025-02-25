import yaml
from datetime import datetime
from typing import List, Dict, Tuple
from langchain.schema import Document
from langchain_community.document_loaders.text import TextLoader

from .base import BaseLoader


class MinimaTextLoader(TextLoader, BaseLoader):
    """Custom loader for Markdown files that extracts YAML frontmatter."""
    
    def __init__(self, file_path: str, **kwargs):
        TextLoader.__init__(self, file_path, **kwargs)
        self.encoding = kwargs.get("encoding", "utf-8")
    
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
