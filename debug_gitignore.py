"""Debug script to test gitignore functionality."""
import tempfile
from pathlib import Path
from backend.services.file_reader import get_project_context

# Create temp directory
temp_dir = tempfile.mkdtemp()
temp_path = Path(temp_dir)

# Create .gitignore
gitignore = temp_path / ".gitignore"
gitignore.write_text("*.log\ntemp/\n__pycache__/", encoding='utf-8')

# Create files
(temp_path / "main.py").write_text("print('hello')", encoding='utf-8')
(temp_path / "debug.log").write_text("log content", encoding='utf-8')

# Create temp directory and file
temp_subdir = temp_path / "temp"
temp_subdir.mkdir()
(temp_subdir / "cache.txt").write_text("cache", encoding='utf-8')

# Create __pycache__ directory and file
pycache_dir = temp_path / "__pycache__"
pycache_dir.mkdir()
(pycache_dir / "module.pyc").write_text("binary", encoding='utf-8')

# Read project
content, result = get_project_context(str(temp_path))

print(f"Files read: {result.files_read}")
print(f"Files skipped: {result.files_skipped}")
print(f"Skipped reasons: {result.skipped_reasons}")
print(f"\nContent preview:\n{content[:500]}")

# Cleanup
import shutil
shutil.rmtree(temp_dir)
