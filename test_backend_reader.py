"""Test the file reader on the actual backend directory."""
from backend.services.file_reader import get_project_context, get_project_summary

# Get summary first
print("=" * 80)
print("PROJECT SUMMARY")
print("=" * 80)
summary = get_project_summary("./backend")
print(f"Total files: {summary['total_files']}")
print(f"Total directories: {summary['total_directories']}")
print(f"File types: {summary['file_types']}")

# Read the backend directory
print("\n" + "=" * 80)
print("READING BACKEND DIRECTORY")
print("=" * 80)
content, result = get_project_context("./backend", max_files=100, max_size_mb=5)

print(f"\nFiles read: {result.files_read}")
print(f"Files skipped: {result.files_skipped}")
print(f"Total size: {result.total_size_bytes / 1024:.2f} KB")
print(f"Skipped reasons: {result.skipped_reasons}")

print("\n" + "=" * 80)
print("CONTENT PREVIEW (first 1000 chars)")
print("=" * 80)
print(content[:1000])

print("\n" + "=" * 80)
print("CONTENT PREVIEW (last 500 chars)")
print("=" * 80)
print(content[-500:])
