from pathlib import Path

from pydantic import ValidationError

from app.schemas.tools import FileAnalyzerInput


class FileAnalyzerToolError(Exception):
    pass


def file_analyzer_tool(tool_input: dict[str, object]) -> str:
    try:
        validated_input = FileAnalyzerInput.model_validate(tool_input)
    except ValidationError as exc:
        raise FileAnalyzerToolError("Invalid file_analyzer tool input.") from exc

    target_path = Path(validated_input.file_path).expanduser().resolve()

    if not target_path.exists():
        raise FileAnalyzerToolError("File does not exist.")
    if not target_path.is_file():
        raise FileAnalyzerToolError("Path is not a file.")

    file_size_bytes = target_path.stat().st_size
    extension = target_path.suffix.lower() or "none"

    try:
        content = target_path.read_text(encoding="utf-8")
        line_count = len(content.splitlines())
        word_count = len(content.split())
        char_count = len(content)
    except UnicodeDecodeError:
        line_count = -1
        word_count = -1
        char_count = -1

    return (
        f"path={target_path}; "
        f"size_bytes={file_size_bytes}; "
        f"extension={extension}; "
        f"line_count={line_count}; "
        f"word_count={word_count}; "
        f"char_count={char_count}"
    )

