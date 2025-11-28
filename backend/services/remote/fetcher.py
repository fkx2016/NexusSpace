"""
Remote Fetcher Service: Handles cloning and managing temporary remote repositories.
"""
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional
from backend.config import TEMP_CLONE_DIR

# Ensure the base temporary directory exists
Path(TEMP_CLONE_DIR).mkdir(parents=True, exist_ok=True)

class RemoteFetcher:
    """
    Clones a repository URL and provides its local path for analysis.
    Automatically cleans up the temporary directory after use.
    """
    def __init__(self):
        self.base_dir = Path(TEMP_CLONE_DIR)

    def _generate_temp_path(self) -> Path:
        """Generates a unique, isolated path for the cloned repository."""
        import uuid
        return self.base_dir / str(uuid.uuid4())

    def clone_repo(self, repo_url: str) -> Optional[Path]:
        """
        Clones the given repository URL to a temporary location.
        Returns the local path or None on failure.
        """
        target_path = self._generate_temp_path()
        target_path.mkdir(parents=True, exist_ok=True)

        print(f"INFO: Cloning {repo_url} to {target_path}...")

        try:
            # Use git subprocess to clone the repository
            subprocess.run(
                ['git', 'clone', '--depth', '1', repo_url, target_path],
                check=True,
                capture_output=True,
                text=True,
                timeout=120  # Timeout for cloning large repos
            )
            print("INFO: Cloning successful.")
            return target_path

        except subprocess.CalledProcessError as e:
            print(f"ERROR: Git clone failed for {repo_url}. Error: {e.stderr}")
            self.cleanup(target_path)
            return None
        except subprocess.TimeoutExpired:
            print(f"ERROR: Git clone timed out after 120s for {repo_url}.")
            self.cleanup(target_path)
            return None

    def cleanup(self, path: Path):
        """Removes the cloned temporary directory."""
        if path.exists() and path.is_dir():
            try:
                # Helper to handle read-only files (common in .git on Windows)
                def on_rm_error(func, path, exc_info):
                    import stat
                    os.chmod(path, stat.S_IWRITE)
                    func(path)
                
                shutil.rmtree(path, onerror=on_rm_error)
                print(f"INFO: Cleaned up temporary directory: {path}")
            except Exception as e:
                print(f"ERROR: Failed to remove temporary directory {path}: {e}")

remote_fetcher = RemoteFetcher() # Instantiate for easy access
