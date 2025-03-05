"""
Tests for the command-line interface.
"""

import os
import sys
import tempfile
from unittest.mock import patch, Mock
from io import StringIO

import pytest

from docu.cli import main, parse_args


class CaptureOutput:
    """Context manager to capture stdout and stderr."""
    def __init__(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        self._stdout_patch = None
        self._stderr_patch = None

    def __enter__(self):
        self._stdout_patch = patch('sys.stdout', self.stdout)
        self._stderr_patch = patch('sys.stderr', self.stderr)
        self._stdout_patch.start()
        self._stderr_patch.start()
        return self

    def __exit__(self, *args):
        self._stdout_patch.stop()
        self._stderr_patch.stop()
        self.stdout.seek(0)
        self.stderr.seek(0)


@pytest.fixture
def sample_python_file():
    """Create a temporary Python file with sample documentation."""
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp:
        tmp.write(
            b"""# Sample module documentation.
# This module demonstrates the documentation format.

# Sample class documentation.
class SampleClass:
    # Sample method documentation.
    def sample_method(self):
        pass

# Sample function documentation.
def sample_function():
    pass
"""
        )
        tmp_path = tmp.name

    yield tmp_path

    # Cleanup
    os.unlink(tmp_path)


def test_parse_args():
    """Test argument parsing directly."""
    # Test default values
    args = parse_args(["/path/to/file.py"])
    assert args.file_path == "/path/to/file.py"
    assert args.format == "html"
    assert args.template == "default"
    assert args.doc_style == "google"
    assert not args.verbose
    assert args.output_dir is None

    # Test with all options
    args = parse_args([
        "/path/to/file.py",
        "--format", "markdown",
        "--output-dir", "/output",
        "--template", "modern",
        "--doc-style", "numpy",
        "--verbose"
    ])
    assert args.file_path == "/path/to/file.py"
    assert args.format == "markdown"
    assert args.output_dir == "/output"
    assert args.template == "modern"
    assert args.doc_style == "numpy"
    assert args.verbose


def test_main_missing_argument():
    """Test behavior when no file path is provided."""
    with CaptureOutput() as captured, pytest.raises(SystemExit):
        main([])
    assert "error: the following arguments are required: file_path" in captured.stderr.getvalue()


def test_main_nonexistent_file():
    """Test behavior with a nonexistent file."""
    with CaptureOutput() as captured:
        result = main(["nonexistent_file.py"])
    assert result != 0
    assert "Error: File not found" in captured.stderr.getvalue()


def test_main_non_python_file(tmp_path):
    """Test behavior with a non-Python file."""
    # Create a non-Python file
    non_py_file = tmp_path / "test.txt"
    non_py_file.write_text("This is not a Python file")

    with CaptureOutput() as captured:
        result = main([str(non_py_file)])
    assert result != 0
    assert "Error:" in captured.stderr.getvalue()
    assert "must be a Python (.py) file" in captured.stderr.getvalue()


@patch("docu.cli.process_file")
def test_main_markdown_output(mock_process_file, sample_python_file):
    """Test generating markdown documentation."""
    mock_process_file.return_value = "# Module\n\nSample module documentation."
    with CaptureOutput() as captured:
        result = main([sample_python_file, "--format", "markdown"])
    assert result == 0
    assert "# Module" in captured.stdout.getvalue()
    assert "Sample module documentation" in captured.stdout.getvalue()


@patch("docu.cli.process_file")
def test_main_html_output(mock_process_file, sample_python_file):
    """Test generating HTML documentation."""
    mock_process_file.return_value = "<html><body>Sample module documentation.</body></html>"
    with CaptureOutput() as captured:
        result = main([sample_python_file, "--format", "html"])
    assert result == 0
    assert "<html" in captured.stdout.getvalue()
    assert "Sample module documentation" in captured.stdout.getvalue()


@patch("docu.cli.process_file")
def test_main_output_dir(mock_process_file, sample_python_file):
    """Test saving documentation to an output directory."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_file = os.path.join(
            tmp_dir, os.path.basename(sample_python_file).replace(".py", ".md")
        )
        mock_process_file.return_value = output_file

        with CaptureOutput() as captured:
            result = main(
                [sample_python_file, "--format", "markdown", "--output-dir", tmp_dir]
            )
        assert result == 0
        assert "Documentation saved to" in captured.stdout.getvalue()
        assert output_file in captured.stdout.getvalue()


@patch("docu.cli.process_file")
def test_main_verbose_flag(mock_process_file, sample_python_file):
    """Test that the verbose flag produces additional output."""
    mock_process_file.return_value = "Documentation content"
    with CaptureOutput() as captured:
        result = main([sample_python_file, "--verbose"])
    assert result == 0
    assert "Processing file:" in captured.stdout.getvalue()
    assert "Output format:" in captured.stdout.getvalue()


@patch("docu.cli.process_file")
def test_main_with_template(mock_process_file, sample_python_file):
    """Test using different HTML templates."""
    mock_process_file.return_value = "<html>Content</html>"
    for template in ["default", "minimal", "modern", "rtd"]:
        mock_process_file.reset_mock()
        result = main(
            [sample_python_file, "--format", "html", "--template", template]
        )
        assert result == 0
        mock_process_file.assert_called_once()
        args, kwargs = mock_process_file.call_args
        assert kwargs["template_name"] == template


@patch("docu.cli.process_file")
def test_main_with_doc_style(mock_process_file, sample_python_file):
    """Test using different documentation styles."""
    mock_process_file.return_value = "<html>Content</html>"
    for style in ["google", "numpy", "sphinx"]:
        mock_process_file.reset_mock()
        result = main(
            [sample_python_file, "--format", "html", "--doc-style", style]
        )
        assert result == 0
        mock_process_file.assert_called_once()
        args, kwargs = mock_process_file.call_args
        assert kwargs["doc_style"] == style


@patch("docu.cli.process_file")
def test_main_exception_handling(mock_process_file, sample_python_file):
    """Test that exceptions are properly handled and reported."""
    # Test different types of exceptions
    for exception in [ValueError("Test error"),
                     FileNotFoundError("File not found"),
                     TypeError("Type error")]:
        mock_process_file.side_effect = exception
        with CaptureOutput() as captured:
            result = main([sample_python_file])
        assert result != 0
        assert "Error:" in captured.stderr.getvalue()
        assert str(exception) in captured.stderr.getvalue()

    # Test with verbose flag - should re-raise the exception
    mock_process_file.side_effect = ValueError("Test error")
    with pytest.raises(ValueError), CaptureOutput():
        main([sample_python_file, "--verbose"])


def test_invalid_format():
    """Test handling of invalid format option."""
    with CaptureOutput() as captured, pytest.raises(SystemExit):
        main(["file.py", "--format", "invalid"])
    assert "invalid choice: 'invalid'" in captured.stderr.getvalue()
    assert "choose from markdown, html" in captured.stderr.getvalue()


@patch("docu.cli.process_file")
def test_invalid_template(mock_process_file):
    """Test handling of invalid template option."""
    mock_process_file.side_effect = ValueError("Invalid template: invalid")
    with CaptureOutput() as captured:
        result = main(["file.py", "--template", "invalid"])
    assert result != 0
    assert "Error:" in captured.stderr.getvalue()


def test_invalid_doc_style():
    """Test handling of invalid doc_style option."""
    with CaptureOutput() as captured, pytest.raises(SystemExit):
        main(["file.py", "--doc-style", "invalid"])
    assert "invalid choice: 'invalid'" in captured.stderr.getvalue()
    assert "choose from google, numpy, sphinx" in captured.stderr.getvalue()
