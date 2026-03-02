"""Tests for document parsing."""

from pathlib import Path

import pytest

from contractguard.parser import extract_text

EXAMPLES_DIR = Path(__file__).parent.parent / "examples"


def test_extract_txt():
    """Test extracting text from a .txt file."""
    text = extract_text(EXAMPLES_DIR / "sample_lease.txt")
    assert "RESIDENTIAL LEASE AGREEMENT" in text
    assert "SECURITY DEPOSIT" in text
    assert len(text) > 100


def test_extract_nonexistent_file():
    """Test error handling for nonexistent file."""
    with pytest.raises(FileNotFoundError):
        extract_text("/nonexistent/path/file.txt")


def test_extract_unsupported_format(tmp_path):
    """Test error handling for unsupported file format."""
    fake_file = tmp_path / "test.xyz"
    fake_file.write_text("hello")
    with pytest.raises(ValueError, match="Unsupported file type"):
        extract_text(fake_file)


def test_extract_nda():
    """Test extracting text from NDA sample."""
    text = extract_text(EXAMPLES_DIR / "sample_nda.txt")
    assert "NON-DISCLOSURE AGREEMENT" in text
    assert "Confidential Information" in text
