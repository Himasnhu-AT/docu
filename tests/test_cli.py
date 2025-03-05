"""
Tests for the command-line interface.
"""

import os
import tempfile
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from docu.cli import main


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


@pytest.fixture
def sample_python_file():
    """Create a temporary Python file with sample #/ documentation."""
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp:
        tmp.write(
            b"""#/ Sample module documentation.

#/ Sample function documentation.
def sample_function():
    pass
"""
        )
        tmp_path = tmp.name

    yield tmp_path

    # Cleanup
    os.unlink(tmp_path)


def test_main_help(runner):
    """Test that the --help option works."""
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Generate documentation from Python files" in result.output


def test_main_missing_argument(runner):
    """Test behavior when no file path is provided."""
    result = runner.invoke(main)
    assert result.exit_code != 0
    assert "Missing argument" in result.output


def test_main_nonexistent_file(runner):
    """Test behavior with a nonexistent file."""
    result = runner.invoke(main, ["nonexistent_file.py"])
    assert result.exit_code != 0
    assert "Error" in result.output


def test_main_non_python_file(runner, tmp_path):
    """Test behavior with a non-Python file."""
    # Create a non-Python file
    non_py_file = tmp_path / "test.txt"
    non_py_file.write_text("This is not a Python file")

    result = runner.invoke(main, [str(non_py_file)])
    assert result.exit_code != 0
    assert "Error" in result.output
    assert "must be a Python (.py) file" in result.output


def test_main_markdown_output(runner, sample_python_file):
    """Test generating markdown documentation."""
    result = runner.invoke(main, [sample_python_file, "--format", "markdown"])
    assert result.exit_code == 0
    assert "# Module" in result.output
    assert "Documentation (Markdown)" in result.output


def test_main_html_output(runner, sample_python_file):
    """Test generating HTML documentation."""
    result = runner.invoke(main, [sample_python_file, "--format", "html"])
    assert result.exit_code == 0
    assert "Generated HTML Documentation" in result.output


def test_main_output_dir(runner, sample_python_file):
    """Test saving documentation to an output directory."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        result = runner.invoke(
            main, [sample_python_file, "--format", "markdown", "--output-dir", tmp_dir]
        )
        assert result.exit_code == 0
        assert "Documentation saved to" in result.output

        # Check that the file was created
        output_file = os.path.join(
            tmp_dir, os.path.basename(sample_python_file).replace(".py", ".md")
        )
        assert os.path.exists(output_file)


def test_main_verbose_flag(runner, sample_python_file):
    """Test that the verbose flag produces additional output."""
    result = runner.invoke(main, [sample_python_file, "--verbose"])
    assert result.exit_code == 0
    assert "Processing file:" in result.output
    assert "Output format:" in result.output


@patch("docu.cli.process_file")
def test_main_exception_handling(mock_process_file, runner, sample_python_file):
    """Test that exceptions are properly handled and reported."""
    mock_process_file.side_effect = ValueError("Test error")

    result = runner.invoke(main, [sample_python_file])
    assert result.exit_code != 0
    assert "Error:" in result.output
    assert "Test error" in result.output