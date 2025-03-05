"""
Tests for the documentation generation functionality.
"""

import os
import tempfile
from pathlib import Path

import pytest

from docu.docgen import process_file
from docu.parsers import extract_doc_comments, parse_python_file
from docu.generators import generate_markdown_docs, generate_html_docs
from docu.models import DocItem

def create_test_file(content: str) -> str:
    """Helper to create a temporary test file."""
    with tempfile.NamedTemporaryFile(suffix=".py", delete=False) as tmp:
        tmp.write(content.encode())
        return tmp.name

@pytest.fixture
def sample_python_file():
    """Create a temporary Python file with sample #/ documentation."""
    content = '''#/ This is a module level documentation comment.
#/ It has multiple lines.

import math

#/ This is a class with documentation.
#/ It also has multiple lines
#/ and explains the purpose.
class Example:
    x: int
    y: str
    
    #/ This is the constructor.
    #/ It takes initial values.
    def __init__(self, value: int, text: str):
        self.value = value
        self.text = text
    
    #/ This is a method.
    #/ It has multiple lines of documentation.
    def method(self, x: float) -> float:
        return self.value * x

#/ This is a function.
#/ With multi-line documentation.
def func(a: int, b: str = "default") -> None:
    pass
'''
    tmp_path = create_test_file(content)
    yield tmp_path
    os.unlink(tmp_path)

@pytest.fixture
def empty_python_file():
    """Create a temporary Python file with no documentation."""
    content = '''
class Example:
    def method(self):
        pass

def func():
    pass
'''
    tmp_path = create_test_file(content)
    yield tmp_path
    os.unlink(tmp_path)

def test_extract_doc_comments(sample_python_file):
    """Test extraction of #/ comments from a Python file."""
    comments = extract_doc_comments(sample_python_file)
    
    # Check number of comments and content
    assert len(comments) == 8
    assert comments[0] == (1, "This is a module level documentation comment.")
    assert comments[1] == (2, "It has multiple lines.")
    
    # Check class documentation
    assert any("This is a class with documentation" in c[1] for c in comments)
    assert any("and explains the purpose" in c[1] for c in comments)
    
    # Check method documentation
    assert any("This is the constructor" in c[1] for c in comments)
    assert any("This is a method" in c[1] for c in comments)

def test_parse_python_file(sample_python_file):
    """Test parsing of Python file into documentation items."""
    doc_items = parse_python_file(sample_python_file)
    
    # Module documentation
    module_name = Path(sample_python_file).stem
    assert module_name in doc_items
    assert doc_items[module_name].item_type == "module"
    assert "module level documentation" in doc_items[module_name].doc
    
    # Class documentation
    assert "Example" in doc_items
    example_class = doc_items["Example"]
    assert example_class.item_type == "class"
    assert "class with documentation" in example_class.doc
    assert example_class.fields == {"x": "int", "y": "str"}
    
    # Constructor and method
    assert len(example_class.methods) == 2
    init_method = next(m for m in example_class.methods if m.name == "__init__")
    assert len(init_method.args) == 2
    assert init_method.args[0].name == "value"
    assert init_method.args[0].type_hint == "int"
    
    method = next(m for m in example_class.methods if m.name == "method")
    assert method.return_type == "float"
    assert method.args[0].name == "x"
    assert method.args[0].type_hint == "float"
    
    # Function documentation
    assert "func" in doc_items
    func = doc_items["func"]
    assert func.item_type == "function"
    assert len(func.args) == 2
    assert func.args[0].name == "a"
    assert func.args[0].type_hint == "int"
    assert func.return_type == "None"

def test_parse_empty_file(empty_python_file):
    """Test parsing a file with no documentation."""
    doc_items = parse_python_file(empty_python_file)
    
    # Should still parse structure but with empty docs
    assert "Example" in doc_items
    assert doc_items["Example"].doc == ""
    assert "func" in doc_items
    assert doc_items["func"].doc == ""

def test_generate_markdown_docs():
    """Test generation of markdown documentation."""
    doc_items = {
        "module": DocItem(
            name="module",
            doc="Module docs\nWith multiple lines",
            item_type="module",
            lineno=1
        ),
        "Class": DocItem(
            name="Class",
            doc="Class docs",
            item_type="class",
            lineno=5,
            fields={"field1": "int", "field2": "str"},
            methods=[
                DocItem(
                    name="method",
                    doc="Method docs",
                    item_type="method",
                    lineno=7,
                    parent="Class",
                    args=[{"name": "arg1", "type_hint": "int"}],
                    return_type="bool"
                )
            ]
        ),
        "function": DocItem(
            name="function",
            doc="Function docs",
            item_type="function",
            lineno=10,
            args=[{"name": "param1", "type_hint": "str"}],
            return_type="None"
        ),
    }
    
    markdown = generate_markdown_docs(doc_items)
    
    # Check main sections
    assert "# Module module" in markdown
    assert "## Classes" in markdown
    assert "### class Class" in markdown
    assert "#### Fields" in markdown
    assert "field1: int" in markdown
    assert "field2: str" in markdown
    assert "#### Methods" in markdown
    assert "##### method" in markdown
    assert "```python" in markdown
    assert "method(arg1: int) -> bool" in markdown
    assert "## Functions" in markdown
    assert "### function" in markdown
    assert "function(param1: str) -> None" in markdown

def test_generate_html_docs():
    """Test generation of HTML documentation."""
    doc_items = {
        "module": DocItem(
            name="module",
            doc="Module docs",
            item_type="module",
            lineno=1
        ),
    }
    
    html = generate_html_docs(doc_items)
    
    # Check basic HTML structure
    assert "<!DOCTYPE html>" in html
    assert "<title>" in html
    assert "Module docs" in html
    
    # Test with different templates
    for template in ["default", "minimal", "modern", "rtd"]:
        html = generate_html_docs(doc_items, template_name=template)
        assert "Module docs" in html

def test_process_file(sample_python_file):
    """Test end-to-end processing of a Python file."""
    # Test markdown output
    md_content = process_file(sample_python_file, output_format="markdown")
    assert "# Module" in md_content
    assert "This is a module level documentation comment" in md_content
    
    # Test HTML output with different templates
    for template in ["default", "minimal", "modern", "rtd"]:
        html_content = process_file(
            sample_python_file,
            output_format="html",
            template_name=template
        )
        assert "<!DOCTYPE html>" in html_content
        assert "This is a module level documentation comment" in html_content
    
    # Test saving to directory
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = process_file(
            sample_python_file,
            output_format="markdown",
            output_dir=tmpdir
        )
        assert os.path.exists(output_path)
        with open(output_path, "r") as f:
            content = f.read()
            assert "# Module" in content

def test_process_file_errors():
    """Test error handling in process_file."""
    # Test nonexistent file
    with pytest.raises(FileNotFoundError):
        process_file("nonexistent_file.py")
    
    # Test invalid output format
    with pytest.raises(ValueError):
        process_file(sample_python_file, output_format="invalid")
    
    # Test invalid template
    with pytest.raises(ValueError):
        process_file(sample_python_file, template_name="nonexistent")

def test_process_file_with_empty_file(empty_python_file):
    """Test processing a file with no documentation."""
    content = process_file(empty_python_file)
    assert content.strip() != ""  # Should still generate something
    assert "# Module" in content  # Should have basic structure