import pytest

from app.tools.file_analyzer import FileAnalyzerToolError, file_analyzer_tool


def test_file_analyzer_tool_returns_metadata_for_text_file(tmp_path) -> None:
    target_file = tmp_path / "sample.txt"
    target_file.write_text("hello world\nthis is a test", encoding="utf-8")

    result = file_analyzer_tool({"file_path": str(target_file)})

    assert "extension=.txt" in result
    assert "line_count=2" in result
    assert "word_count=6" in result
    assert "char_count=26" in result


def test_file_analyzer_tool_rejects_missing_file() -> None:
    with pytest.raises(FileAnalyzerToolError, match="does not exist"):
        file_analyzer_tool({"file_path": "missing_file.txt"})


def test_file_analyzer_tool_rejects_directory_path(tmp_path) -> None:
    with pytest.raises(FileAnalyzerToolError, match="not a file"):
        file_analyzer_tool({"file_path": str(tmp_path)})


def test_file_analyzer_tool_rejects_invalid_input() -> None:
    with pytest.raises(FileAnalyzerToolError, match="Invalid file_analyzer tool input"):
        file_analyzer_tool({"file_path": 123})

