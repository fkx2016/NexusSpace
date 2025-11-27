"""File reader service for analyzing local codebases.

This module provides functionality to read and concatenate files from a project directory
while respecting .gitignore patterns and applying safety limits.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import pathspec
from ..config import MAX_FILES_TO_READ, MAX_CODEBASE_SIZE_MB, SUPPORTED_EXTENSIONS


class FileReaderResult:
    """Result of reading a project directory."""
    
    def __init__(
        self,
        content: str,
        files_read: int,
        files_skipped: int,
        total_size_bytes: int,
        skipped_reasons: Dict[str, int]
    ):
        self.content = content
        self.files_read = files_read
        self.files_skipped = files_skipped
        self.total_size_bytes = total_size_bytes
        self.skipped_reasons = skipped_reasons
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "files_read": self.files_read,
            "files_skipped": self.files_skipped,
            "total_size_bytes": self.total_size_bytes,
            "total_size_mb": round(self.total_size_bytes / (1024 * 1024), 2),
            "skipped_reasons": self.skipped_reasons
        }


def load_gitignore_patterns(root_path: Path) -> pathspec.PathSpec:
    """
    Load .gitignore patterns from the project root.
    
    Args:
        root_path: Root directory of the project
        
    Returns:
        PathSpec object for matching ignored files
    """
    gitignore_path = root_path / ".gitignore"
    patterns = []
    
    # Add default patterns to always ignore
    default_ignores = [
        ".git/",
        ".git/**",
        "__pycache__/",
        "*.pyc",
        "*.pyo",
        "*.pyd",
        ".Python",
        "node_modules/",
        ".venv/",
        "venv/",
        "env/",
        "ENV/",
        ".env",
        "*.egg-info/",
        "dist/",
        "build/",
        ".pytest_cache/",
        ".mypy_cache/",
        ".coverage",
        "htmlcov/",
        ".DS_Store",
        "Thumbs.db",
    ]
    patterns.extend(default_ignores)
    
    # Load patterns from .gitignore if it exists
    if gitignore_path.exists():
        try:
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except Exception as e:
            print(f"Warning: Could not read .gitignore: {e}")
    
    return pathspec.PathSpec.from_lines('gitwildmatch', patterns)


def is_text_file(file_path: Path) -> bool:
    """
    Check if a file is likely a text file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file appears to be text, False otherwise
    """
    # First check extension
    if file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
        return True
    
    # For files without recognized extensions, try to read a sample
    try:
        with open(file_path, 'rb') as f:
            # Read first 8KB
            chunk = f.read(8192)
            if not chunk:
                return True  # Empty file, treat as text
            
            # Check for null bytes (common in binary files)
            if b'\x00' in chunk:
                return False
            
            # Try to decode as UTF-8
            try:
                chunk.decode('utf-8')
                return True
            except UnicodeDecodeError:
                return False
    except Exception:
        return False


def read_file_content(file_path: Path) -> Optional[str]:
    """
    Read the content of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File content as string, or None if reading failed
    """
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()
    except Exception as e:
        print(f"Warning: Could not read {file_path}: {e}")
        return None


def get_project_context(
    root_path: str,
    max_files: int = MAX_FILES_TO_READ,
    max_size_mb: int = MAX_CODEBASE_SIZE_MB
) -> Tuple[str, FileReaderResult]:
    """
    Read and concatenate files from a project directory.
    
    This function walks through a directory tree, respects .gitignore patterns,
    and concatenates text files into a single string with clear file demarcation.
    
    Args:
        root_path: Root directory of the project to analyze
        max_files: Maximum number of files to read (safety limit)
        max_size_mb: Maximum total size in MB (safety limit)
        
    Returns:
        Tuple of (concatenated_content, FileReaderResult with metadata)
        
    Raises:
        ValueError: If root_path doesn't exist or is not a directory
    """
    root = Path(root_path).resolve()
    
    # Validate root path
    if not root.exists():
        raise ValueError(f"Path does not exist: {root_path}")
    if not root.is_dir():
        raise ValueError(f"Path is not a directory: {root_path}")
    
    # Load gitignore patterns
    gitignore_spec = load_gitignore_patterns(root)
    
    # Track statistics
    files_read = 0
    files_skipped = 0
    total_size_bytes = 0
    max_size_bytes = max_size_mb * 1024 * 1024
    skipped_reasons: Dict[str, int] = {}
    
    # Collect file contents
    file_contents: List[Tuple[str, str]] = []  # (relative_path, content)
    
    # Walk the directory tree
    for current_dir, dirs, files in os.walk(root):
        current_path = Path(current_dir)
        rel_dir = current_path.relative_to(root)
        
        # Filter out ignored directories (modifies dirs in-place to prevent traversal)
        dirs[:] = [
            d for d in dirs
            if not gitignore_spec.match_file(str(rel_dir / d) + '/')
        ]
        
        # Process files
        for filename in sorted(files):
            file_path = current_path / filename
            rel_path = file_path.relative_to(root)
            rel_path_str = str(rel_path).replace('\\', '/')
            
            # Check if file is ignored
            if gitignore_spec.match_file(rel_path_str):
                files_skipped += 1
                skipped_reasons['gitignore'] = skipped_reasons.get('gitignore', 0) + 1
                continue
            
            # Check if we've hit the file limit
            if files_read >= max_files:
                files_skipped += 1
                skipped_reasons['max_files_limit'] = skipped_reasons.get('max_files_limit', 0) + 1
                continue
            
            # Check if it's a text file
            if not is_text_file(file_path):
                files_skipped += 1
                skipped_reasons['binary_or_unsupported'] = skipped_reasons.get('binary_or_unsupported', 0) + 1
                continue
            
            # Check file size
            try:
                file_size = file_path.stat().st_size
            except Exception:
                files_skipped += 1
                skipped_reasons['stat_error'] = skipped_reasons.get('stat_error', 0) + 1
                continue
            
            # Check if adding this file would exceed size limit
            if total_size_bytes + file_size > max_size_bytes:
                files_skipped += 1
                skipped_reasons['max_size_limit'] = skipped_reasons.get('max_size_limit', 0) + 1
                continue
            
            # Read the file
            content = read_file_content(file_path)
            if content is None:
                files_skipped += 1
                skipped_reasons['read_error'] = skipped_reasons.get('read_error', 0) + 1
                continue
            
            # Add to collection
            file_contents.append((rel_path_str, content))
            files_read += 1
            total_size_bytes += file_size
    
    # Build the concatenated output
    output_parts = []
    for rel_path, content in file_contents:
        output_parts.append(f"--- START FILE: {rel_path} ---")
        output_parts.append(content)
        output_parts.append(f"--- END FILE: {rel_path} ---")
        output_parts.append("")  # Empty line between files
    
    concatenated_content = "\n".join(output_parts)
    
    # Create result object
    result = FileReaderResult(
        content=concatenated_content,
        files_read=files_read,
        files_skipped=files_skipped,
        total_size_bytes=total_size_bytes,
        skipped_reasons=skipped_reasons
    )
    
    return concatenated_content, result


def get_project_summary(root_path: str) -> Dict:
    """
    Get a quick summary of a project without reading all files.
    
    Args:
        root_path: Root directory of the project
        
    Returns:
        Dictionary with project statistics
    """
    root = Path(root_path).resolve()
    
    if not root.exists() or not root.is_dir():
        return {"error": "Invalid path"}
    
    gitignore_spec = load_gitignore_patterns(root)
    
    total_files = 0
    total_dirs = 0
    file_types: Dict[str, int] = {}
    
    for current_dir, dirs, files in os.walk(root):
        current_path = Path(current_dir)
        rel_dir = current_path.relative_to(root)
        
        # Filter ignored directories
        dirs[:] = [
            d for d in dirs
            if not gitignore_spec.match_file(str(rel_dir / d) + '/')
        ]
        
        total_dirs += len(dirs)
        
        for filename in files:
            file_path = current_path / filename
            rel_path = file_path.relative_to(root)
            rel_path_str = str(rel_path).replace('\\', '/')
            
            if gitignore_spec.match_file(rel_path_str):
                continue
            
            total_files += 1
            ext = file_path.suffix.lower() or 'no_extension'
            file_types[ext] = file_types.get(ext, 0) + 1
    
    return {
        "total_files": total_files,
        "total_directories": total_dirs,
        "file_types": file_types,
        "root_path": str(root)
    }
