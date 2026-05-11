from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from app.services.document_text_service import (
    DocumentTextExtractionError,
    extract_document_text,
)


def test_extracts_text_file_content(tmp_path: Path) -> None:
    text_path = tmp_path / "policy.txt"
    text_path.write_text("Refunds are available within 7 days.", encoding="utf-8")

    text = extract_document_text(str(text_path), ".txt")

    assert text == "Refunds are available within 7 days."


def test_extracts_markdown_file_content(tmp_path: Path) -> None:
    markdown_path = tmp_path / "policy.md"
    markdown_path.write_text("# Policy\nRefunds are available.", encoding="utf-8")

    text = extract_document_text(str(markdown_path), ".md")

    assert "Refunds are available." in text


def test_rejects_empty_text_file(tmp_path: Path) -> None:
    text_path = tmp_path / "empty.txt"
    text_path.write_text("   ", encoding="utf-8")

    with pytest.raises(DocumentTextExtractionError, match="No text could be extracted"):
        extract_document_text(str(text_path), ".txt")


def test_returns_controlled_error_for_missing_file(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.txt"

    with pytest.raises(DocumentTextExtractionError, match="could not be read"):
        extract_document_text(str(missing_path), ".txt")


def test_extracts_pdf_text_with_pypdf(tmp_path: Path) -> None:
    pdf_path = tmp_path / "policy.pdf"
    pdf_path.write_bytes(b"%PDF-pretend")
    first_page = Mock()
    first_page.extract_text.return_value = "Refund policy."
    second_page = Mock()
    second_page.extract_text.return_value = "Cancellation policy."

    with patch("app.services.document_text_service.PdfReader") as pdf_reader:
        pdf_reader.return_value.pages = [first_page, second_page]

        text = extract_document_text(str(pdf_path), ".pdf")

    assert "Refund policy." in text
    assert "Cancellation policy." in text


def test_rejects_pdf_without_extractable_text(tmp_path: Path) -> None:
    pdf_path = tmp_path / "empty.pdf"
    pdf_path.write_bytes(b"%PDF-pretend")
    page = Mock()
    page.extract_text.return_value = ""

    with patch("app.services.document_text_service.PdfReader") as pdf_reader:
        pdf_reader.return_value.pages = [page]

        with pytest.raises(DocumentTextExtractionError, match="No text could be extracted"):
            extract_document_text(str(pdf_path), ".pdf")


def test_rejects_unsupported_extension(tmp_path: Path) -> None:
    docx_path = tmp_path / "policy.docx"
    docx_path.write_bytes(b"docx")

    with pytest.raises(DocumentTextExtractionError, match="Unsupported document extension"):
        extract_document_text(str(docx_path), ".docx")
