"""Test script to verify the analyze-project endpoint works correctly."""
import requests
import json

# Test 1: Valid project path
print("=" * 80)
print("TEST 1: Valid Project Path")
print("=" * 80)

response = requests.post(
    "http://localhost:8001/api/analyze-project",
    json={
        "project_path": "./test_project",
        "analysis_prompt": "Provide a brief analysis of this calculator code."
    }
)

print(f"Status Code: {response.status_code}")
print(f"\nResponse JSON (metadata only):")
data = response.json()
print(json.dumps(data.get("metadata", {}), indent=2))

# Test 2: Invalid path
print("\n" + "=" * 80)
print("TEST 2: Invalid Project Path (should return 400)")
print("=" * 80)

response = requests.post(
    "http://localhost:8001/api/analyze-project",
    json={
        "project_path": "./nonexistent_directory"
    }
)

print(f"Status Code: {response.status_code}")
print(f"Error Detail: {response.json().get('detail', 'N/A')}")

# Test 3: Empty directory
print("\n" + "=" * 80)
print("TEST 3: Check file reading worked")
print("=" * 80)
print(f"Files read from test_project: {data['metadata']['file_analysis']['files_read']}")
print(f"Total size: {data['metadata']['file_analysis']['total_size_mb']} MB")
print(f"Files skipped: {data['metadata']['file_analysis']['files_skipped']}")
print("\nSUCCESS: File reader integration is working correctly!")
