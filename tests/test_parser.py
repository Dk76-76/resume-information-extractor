"""Tests for PDF and DOCX document parser."""

from pathlib import Path
import pytest

from app.parser import (
    CorruptedFileError,
    DocumentParserError,
    EmptyDocumentError,
    NoTextFoundError,
    UnsupportedFileTypeError,
    extract_text_from_file,
)

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"


def test_parse_valid_pdf():
    """Verify that text is extracted from a valid PDF sample."""
    sample_pdf = SAMPLES_DIR / "resume_1.pdf"
    assert sample_pdf.exists(), "Sample resume_1.pdf must exist"
    
    file_bytes = sample_pdf.read_bytes()
    text = extract_text_from_file(file_bytes, "resume_1.pdf")
    
    assert len(text) > 50
    assert "Aarav Sharma" in text
    assert "aarav.sharma@example.com" in text
    assert "EDUCATION" in text


def test_parse_valid_docx():
    """Verify that text is extracted from a valid DOCX sample."""
    sample_docx = SAMPLES_DIR / "resume_2.docx"
    assert sample_docx.exists(), "Sample resume_2.docx must exist"
    
    file_bytes = sample_docx.read_bytes()
    text = extract_text_from_file(file_bytes, "resume_2.docx")
    
    assert len(text) > 50
    assert "Sarah Jenkins" in text
    assert "sarah.jenkins@techmail.org" in text
    assert "Work Experience" in text


def test_parse_empty_file():
    """Empty 0-byte file must raise EmptyDocumentError."""
    with pytest.raises(EmptyDocumentError):
        extract_text_from_file(b"", "empty.pdf")
        
    with pytest.raises(EmptyDocumentError):
        extract_text_from_file(b"   ", "empty.docx")


def test_parse_unsupported_extension():
    """Non-PDF/DOCX file extension must raise UnsupportedFileTypeError."""
    with pytest.raises(UnsupportedFileTypeError):
        extract_text_from_file(b"some content", "resume.txt")
        
    with pytest.raises(UnsupportedFileTypeError):
        extract_text_from_file(b"some content", "resume.png")


def test_parse_corrupted_pdf():
    """Corrupted binary data masquerading as PDF must raise CorruptedFileError."""
    fake_pdf = b"%PDF-1.4\nCorrupted binary rubbish that cannot be parsed as valid PDF"
    with pytest.raises(CorruptedFileError):
        extract_text_from_file(fake_pdf, "corrupted.pdf")


def test_parse_corrupted_docx():
    """Corrupted binary data masquerading as DOCX must raise CorruptedFileError."""
    fake_docx = b"Not a real docx zip archive"
    with pytest.raises(CorruptedFileError):
        extract_text_from_file(fake_docx, "corrupted.docx")
