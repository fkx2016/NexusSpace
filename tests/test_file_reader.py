"""Unit tests for the file reader service."""

import os
import tempfile
from pathlib import Path
import pytest
from backend.services.file_reader import (
    get_project_context,
    get_project_summary,
    load_gitignore_patterns,
    is_text_file,
)


class TestFileReader:
    """Test suite for file reader functionality."""
    
    def setup_method(self):
        """Create a temporary directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)
    
    def teardown_method(self):
        """Clean up temporary directory after each test."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_file(self, relative_path: str, content: str):
        """Helper to create a file in the temp directory."""
        file_path = self.temp_path / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding='utf-8')
        return file_path
    
    def test_simple_project_reading(self):
        """Test reading a simple project with a few files."""
        # Create test files
        self.create_file("main.py", "print('hello world')")
        self.create_file("utils.py", "def helper():\n    pass")
        self.create_file("README.md", "# Test Project")
        
        # Read project
        content, result = get_project_context(self.temp_dir)
        
        # Verify all files were read
        assert result.files_read == 3
        assert result.files_skipped == 0
        
        # Verify content format
        assert "--- START FILE: main.py ---" in content
        assert "print('hello world')" in content
        assert "--- END FILE: main.py ---" in content
        
        assert "--- START FILE: utils.py ---" in content
        assert "def helper():" in content
        
        assert "--- START FILE: README.md ---" in content
        assert "# Test Project" in content
    
    def test_gitignore_respected(self):
        """Test that .gitignore patterns are respected."""
        # Create .gitignore
        self.create_file(".gitignore", "*.log\ntemp/\n__pycache__/")
        
        # Create files
        self.create_file("main.py", "print('hello')")
        self.create_file("debug.log", "log content")  # Should be ignored
        self.create_file("temp/cache.txt", "cache")  # Should be ignored (directory not traversed)
        self.create_file("__pycache__/module.pyc", "binary")  # Should be ignored (directory not traversed)
        
        # Read project
        content, result = get_project_context(self.temp_dir)
        
        # Only main.py should be read (.gitignore itself is also read)
        assert result.files_read == 2  # main.py + .gitignore
        # debug.log is skipped at file level; temp/ and __pycache__/ are filtered at directory level
        assert result.files_skipped >= 1  # At least debug.log
        
        # Verify ignored files are not in content
        assert "debug.log" not in content
        assert "cache.txt" not in content
        assert "module.pyc" not in content
        
        # Verify main.py is in content
        assert "main.py" in content
        assert "print('hello')" in content
    
    def test_nested_directories(self):
        """Test reading files from nested directory structures."""
        # Create nested structure
        self.create_file("src/main.py", "# main")
        self.create_file("src/utils/helper.py", "# helper")
        self.create_file("tests/test_main.py", "# test")
        
        # Read project
        content, result = get_project_context(self.temp_dir)
        
        # All files should be read
        assert result.files_read == 3
        
        # Verify paths are preserved
        assert "src/main.py" in content
        assert "src/utils/helper.py" in content
        assert "tests/test_main.py" in content
    
    def test_max_files_limit(self):
        """Test that max_files limit is respected."""
        # Create more files than the limit
        for i in range(10):
            self.create_file(f"file_{i}.py", f"# File {i}")
        
        # Read with low limit
        content, result = get_project_context(self.temp_dir, max_files=5)
        
        # Should only read 5 files
        assert result.files_read == 5
        assert result.files_skipped == 5
        assert 'max_files_limit' in result.skipped_reasons
    
    def test_max_size_limit(self):
        """Test that max_size_mb limit is respected."""
        # Create a large file (simulated with smaller limit)
        large_content = "x" * 1024 * 100  # 100KB
        self.create_file("large.txt", large_content)
        self.create_file("small.txt", "small")
        
        # Read with very small size limit (0.05 MB = 50KB)
        content, result = get_project_context(self.temp_dir, max_size_mb=0.05)
        
        # Should skip the large file
        assert result.files_skipped > 0
        assert 'max_size_limit' in result.skipped_reasons or result.files_read < 2
    
    def test_binary_files_skipped(self):
        """Test that binary files are skipped."""
        # Create text file
        self.create_file("text.py", "print('hello')")
        
        # Create binary file
        binary_path = self.temp_path / "image.png"
        binary_path.write_bytes(b'\x89PNG\r\n\x1a\n\x00\x00\x00')
        
        # Read project
        content, result = get_project_context(self.temp_dir)
        
        # Only text file should be read
        assert "text.py" in content
        assert "image.png" not in content
        assert result.skipped_reasons.get('binary_or_unsupported', 0) > 0
    
    def test_file_demarcation_format(self):
        """Test that files are properly demarcated in output."""
        self.create_file("file1.py", "content1")
        self.create_file("file2.py", "content2")
        
        content, result = get_project_context(self.temp_dir)
        
        # Check format
        assert "--- START FILE: file1.py ---" in content
        assert "--- END FILE: file1.py ---" in content
        assert "--- START FILE: file2.py ---" in content
        assert "--- END FILE: file2.py ---" in content
        
        # Verify order (files should be in sorted order)
        start1 = content.index("--- START FILE: file1.py ---")
        end1 = content.index("--- END FILE: file1.py ---")
        start2 = content.index("--- START FILE: file2.py ---")
        
        assert start1 < end1 < start2
    
    def test_project_summary(self):
        """Test the project summary function."""
        # Create test files
        self.create_file("main.py", "# main")
        self.create_file("utils.py", "# utils")
        self.create_file("README.md", "# readme")
        self.create_file("data.json", "{}")
        
        # Get summary
        summary = get_project_summary(self.temp_dir)
        
        # Verify summary
        assert summary['total_files'] == 4
        assert '.py' in summary['file_types']
        assert summary['file_types']['.py'] == 2
        assert '.md' in summary['file_types']
        assert '.json' in summary['file_types']
    
    def test_empty_directory(self):
        """Test reading an empty directory."""
        content, result = get_project_context(self.temp_dir)
        
        assert result.files_read == 0
        assert result.files_skipped == 0
        assert content == ""
    
    def test_invalid_path(self):
        """Test that invalid paths raise ValueError."""
        with pytest.raises(ValueError, match="does not exist"):
            get_project_context("/nonexistent/path")
        
        # Test file instead of directory
        file_path = self.create_file("test.txt", "content")
        with pytest.raises(ValueError, match="not a directory"):
            get_project_context(str(file_path))
    
    def test_default_gitignore_patterns(self):
        """Test that default patterns like __pycache__ are always ignored."""
        # Don't create .gitignore, but create files that should be ignored by default
        self.create_file("main.py", "# main")
        self.create_file("__pycache__/module.pyc", "binary")
        self.create_file("node_modules/package.json", "{}")
        self.create_file(".env", "SECRET=key")
        
        content, result = get_project_context(self.temp_dir)
        
        # Only main.py should be read
        assert result.files_read == 1
        assert "main.py" in content
        assert "__pycache__" not in content
        assert "node_modules" not in content
        assert ".env" not in content


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
