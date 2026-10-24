"""
Sanity tests for project structure initialization.
Compatible with both pytest and python's built-in unittest module.
"""

import unittest
from pathlib import Path


class TestProjectStructure(unittest.TestCase):
    """Test case to ensure initial project skeleton and files are present."""

    def setUp(self):
        self.root = Path(__file__).resolve().parent.parent

    def test_required_directories_exist(self):
        """Verify that expected top-level packages and directories exist."""
        expected_dirs = ["database", "retrieval", "docs", "tests"]
        for dirname in expected_dirs:
            dir_path = self.root / dirname
            self.assertTrue(dir_path.is_dir(), f"Expected directory '{dirname}' is missing.")

    def test_required_files_exist(self):
        """Verify that essential configuration, documentation, and scaffold files exist."""
        expected_files = [
            "requirements.txt",
            ".env.example",
            ".gitignore",
            "README.md",
            "docs/architecture.md",
            "database/__init__.py",
            "database/connection.py",
            "database/models.py",
            "retrieval/__init__.py",
            "tests/test_database_connection.py",
        ]
        for rel_path in expected_files:
            file_path = self.root / rel_path
            self.assertTrue(file_path.is_file(), f"Expected file '{rel_path}' does not exist.")


if __name__ == "__main__":
    unittest.main()
