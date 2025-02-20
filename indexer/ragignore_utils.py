import os
import fnmatch
import logging
from pathlib import Path
from typing import List, Set

logger = logging.getLogger(__name__)

def load_ragignore(root_path: str) -> List[str]:
    """
    Loads ignore patterns from .ragignore file in the given root path.
    Returns a list of patterns to ignore.
    """
    ignore_patterns = []
    ragignore_path = os.path.join(root_path, '.ragignore')
    
    if os.path.isfile(ragignore_path):
        logger.info(f"Found .ragignore file at {ragignore_path}")
        try:
            with open(ragignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue
                    ignore_patterns.append(line)
            logger.info(f"Loaded {len(ignore_patterns)} ignore patterns from .ragignore")
        except Exception as e:
            logger.error(f"Error reading .ragignore file: {e}")
    else:
        logger.info(f"No .ragignore file found at {ragignore_path}")
    
    return ignore_patterns

def should_ignore_path(path: str, ignore_patterns: List[str]) -> bool:
    """
    Determines if a path should be ignored based on the ignore patterns.
    Supports both exact matches and glob-style patterns.
    """
    # Get the relative path from the root
    if not ignore_patterns:
        return False
    
    # Get base name and normalized path
    base_name = os.path.basename(path)
    norm_path = os.path.normpath(path)
    
    for pattern in ignore_patterns:
        # Check for exact directory/file name match
        if base_name == pattern:
            logger.debug(f"Ignoring {path} - exact match with pattern: {pattern}")
            return True
            
        # Check if pattern matches the path using glob pattern
        if fnmatch.fnmatch(base_name, pattern):
            logger.debug(f"Ignoring {path} - glob match with pattern: {pattern}")
            return True
            
        # Check if any parent directory matches the pattern
        path_parts = Path(norm_path).parts
        for part in path_parts:
            if part == pattern or fnmatch.fnmatch(part, pattern):
                logger.debug(f"Ignoring {path} - directory component match: {part} with pattern: {pattern}")
                return True
    
    return False
