from pathlib import Path

from pypdf import PdfReader


class DocumentTextExtractionError(Exception):
    pass


def _ensure_non_empty_text(text: str) -> str:
    cleaned_text = text.strip()
    if not cleaned_text:
        raise DocumentTextExtractionError("No text could be extracted from the document.")
    return cleaned_text


def _extract_text_file(path: Path) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise DocumentTextExtractionError(
            "Document encoding is not supported (use UTF-8)."
        ) from exc
    except OSError as exc:
        raise DocumentTextExtractionError("Document file could not be read.") from exc

    return _ensure_non_empty_text(text)


def _extract_pdf_file(path: Path) -> str:
    try:
        reader = PdfReader(str(path))
        page_text = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:
        raise DocumentTextExtractionError("PDF text could not be extracted.") from exc

    return _ensure_non_empty_text("\n".join(page_text))


def extract_document_text(storage_path: str, file_extension: str) -> str:
    path = Path(storage_path)
    extension = file_extension.lower()

    if extension in {".txt", ".md"}:
        return _extract_text_file(path)

    if extension == ".pdf":
        return _extract_pdf_file(path)

    raise DocumentTextExtractionError(
        f"Unsupported document extension for text extraction: {file_extension}"
    )
