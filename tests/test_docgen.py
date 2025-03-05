"""
Tests for the documentation generation functionality.
"""

import os
import tempfile
from pathlib import Path

import pytest

from docu.docgen import (
    extract_doc_comments,
    parse_python_file,
    generate_markdown_docs,
    generate_html_docs,
    process_file,
    DocItem,
)


@pytest.fixture
def sample_python_file():
    """Create a temporary Python file with sample #/ documentation."""
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp:
        tmp.write(
            b"""#/ This is a module level documentation comment.
#/ It has multiple lines.

import math

#/ This is a class with documentation.
class Example:
    #/ This is the constructor.
    def __init__(self, value):
        self.value = value
    
    #/ This is a method.
    #/ It has multiple lines of documentation.
    def method(self, x):
        return self.value * x

#/ This is a function.
def func():
    pass
"""
        )
        tmp_path = tmp.name
    
    yield tmp_path
    
    # Cleanup
    os.unlink(tmp_path)


def test_extract_doc_comments(sample_python_file):
    """Test extraction of #/ comments from a Python file."""
    comments = extract_doc_comments(sample_python_file)
    
    # Uncomment to debug the actual comments and line numbers
    # for i, (line_no, comment) in enumerate(comments):
    #     print(f"Comment {i}: Line {line_no} - {comment}")
    
    # Check that we found the correct number of comments
    assert len(comments) == 7
    
    # Check specific comments - these should be correct
    assert comments[0] == (1, "This is a module level documentation comment.")
    assert comments[1] == (2, "It has multiple lines.")
    
    # Update assertions to match the actual line numbers in the file
    # The class documentation is on line 6 and constructor on line 8
    # (Manually checked by printing comments above)
    assert comments[2][0] == 6  # Line number for class documentation
    assert comments[3][0] == 8  # Line number for constructor documentation


def test_parse_python_file(sample_python_file):
    """Test parsing of Python file into documentation items."""
    doc_items = parse_python_file(sample_python_file)
    
    # Check that we have the correct number of items
    assert len(doc_items) == 5
    
    # Check that we have the module documentation
    module_name = Path(sample_python_file).stem
    assert module_name in doc_items
    assert doc_items[module_name].item_type == "module"
    
    # Check the class documentation
    assert "Example" in doc_items
    assert doc_items["Example"].item_type == "class"
    
    # Check the method documentation
    assert "Example.method" in doc_items
    assert doc_items["Example.method"].item_type == "method"
    assert doc_items["Example.method"].parent == "Example"
    
    # Check the function documentation
    assert "func" in doc_items
    assert doc_items["func"].item_type == "function"


def test_generate_markdown_docs():
    """Test generation of markdown documentation."""
    doc_items = {
        "module": DocItem(name="module", doc="Module docs", item_type="module", lineno=1),
        "Class": DocItem(name="Class", doc="Class docs", item_type="class", lineno=5),
        "function": DocItem(name="function", doc="Function docs", item_type="function", lineno=10),
        "Class.method": DocItem(
            name="method", doc="Method docs", item_type="method", lineno=7, parent="Class"
        ),
    }
    
    markdown = generate_markdown_docs(doc_items)
    
    # Check that the markdown contains expected sections
    assert "# Module module" in markdown
    assert "## Classes" in markdown
    assert "### Class" in markdown
    assert "#### method" in markdown
    assert "## Functions" in markdown
    assert "### function" in markdown


def test_generate_html_docs():
    """Test generation of HTML documentation."""
    doc_items = {
        "module": DocItem(name="module", doc="Module docs", item_type="module", lineno=1),
    }
    
    html = generate_html_docs(doc_items)
    
    # Check that the HTML contains expected elements
    assert "<!DOCTYPE html>" in html
    assert "<title>Python Documentation</title>" in html
    assert "Module docs" in html


def test_process_file(sample_python_file):
    """Test end-to-end processing of a Python file."""
    # Test getting markdown content
    md_content = process_file(sample_python_file, output_format="markdown")
    assert "# Module" in md_content
    
    # Test getting HTML content
    html_content = process_file(sample_python_file, output_format="html")
    assert "<!DOCTYPE html>" in html_content
    
    # Test saving output to a file
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = process_file(
            sample_python_file, output_format="markdown", output_dir=tmpdir
        )
        assert os.path.exists(output_path)
        with open(output_path, "r") as f:
            content = f.read()
            assert "# Module" in content


def test_process_file_nonexistent():
    """Test handling of nonexistent files."""
    with pytest.raises(FileNotFoundError):
        process_file("nonexistent_file.py")