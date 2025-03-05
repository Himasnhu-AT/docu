"""Tests for template manager and documentation style parsers."""
import pytest
from pathlib import Path
from docu.template_manager import TemplateManager
from docu.doc_parsers import get_parser, GoogleStyleParser, NumpyStyleParser, SphinxStyleParser

def test_template_manager_initialization():
    """Test template manager initialization."""
    tm = TemplateManager()
    assert tm.templates_dir.exists()
    assert (tm.templates_dir / 'default.html').exists()
    assert (tm.templates_dir / 'schema.json').exists()

def test_template_list():
    """Test listing available templates."""
    tm = TemplateManager()
    templates = tm.list_templates()
    
    # Verify all expected templates are present
    template_names = {t['name'] for t in templates}
    assert {'default', 'minimal', 'modern', 'rtd'}.issubset(template_names)
    
    # Check template properties
    for template in templates:
        assert 'name' in template
        assert 'description' in template
        assert 'doc_style' in template

def test_template_validation():
    """Test template validation against schema."""
    tm = TemplateManager()
    valid_template = {
        "name": "test",
        "template": "test.html",
        "description": "Test template",
        "docstyle": "google"
    }
    assert tm.validate_template(valid_template)

    # Test missing required field
    with pytest.raises(ValueError, match="Missing required fields"):
        invalid_template = {
            "name": "test",
            "template": "test.html"
        }
        tm.validate_template(invalid_template)

    # Test invalid docstyle
    with pytest.raises(ValueError, match="Invalid value for docstyle"):
        invalid_template = {
            "name": "test",
            "template": "test.html",
            "description": "Test",
            "docstyle": "invalid"
        }
        tm.validate_template(invalid_template)

def test_template_not_found():
    """Test error handling for non-existent templates."""
    tm = TemplateManager()
    with pytest.raises(ValueError, match="Template 'nonexistent' not found"):
        tm.get_template('nonexistent')

def test_google_style_parser():
    """Test Google style docstring parser."""
    parser = get_parser('google')
    docstring = '''Convert markdown to HTML.

    Args:
        text: Markdown text to convert
        options: Conversion options

    Returns:
        HTML string

    Raises:
        ValueError: If text is empty
    '''
    
    result = parser.parse(docstring)
    assert 'description' in result
    assert 'args' in result
    assert 'returns' in result
    assert 'raises' in result
    assert len(result['args']) == 2

def test_numpy_style_parser():
    """Test NumPy style docstring parser."""
    parser = get_parser('numpy')
    docstring = '''Convert markdown to HTML.

    Parameters
    ----------
    text : str
        Markdown text to convert
    options : dict
        Conversion options

    Returns
    -------
    str
        HTML string

    Raises
    ------
    ValueError
        If text is empty
    '''
    
    result = parser.parse(docstring)
    assert 'description' in result
    assert 'parameters' in result
    assert 'returns' in result
    assert 'raises' in result

def test_sphinx_style_parser():
    """Test Sphinx style docstring parser."""
    parser = get_parser('sphinx')
    docstring = '''Convert markdown to HTML.

    :param text: Markdown text to convert
    :param options: Conversion options
    :returns: HTML string
    :raises ValueError: If text is empty
    '''
    
    result = parser.parse(docstring)
    assert 'description' in result
    assert 'params' in result
    assert 'returns' in result
    assert 'raises' in result

def test_invalid_parser_style():
    """Test error on invalid parser style."""
    with pytest.raises(ValueError):
        get_parser('invalid_style')

def test_all_template_files_exist():
    """Test that all required template files exist and are valid."""
    tm = TemplateManager()
    templates = tm.list_templates()
    
    for template in templates:
        name = template['name']
        # Check HTML file exists
        assert (tm.templates_dir / f"{name}.html").exists()
        # Check JSON config exists (except for default)
        if name != 'default':
            assert (tm.templates_dir / f"{name}.json").exists()

def test_template_rendering():
    """Test that all templates can render basic content."""
    tm = TemplateManager()
    templates = tm.list_templates()
    
    test_data = {
        'title': 'Test Documentation',
        'module_items': [{'name': 'test_module', 'doc': 'Test module doc'}],
        'classes': [{'name': 'TestClass', 'doc': 'Test class doc', 'methods': []}],
        'functions': [{'name': 'test_func', 'doc': 'Test function doc', 'args': []}]
    }
    
    for template in templates:
        name = template['name']
        tmpl = tm.get_template(name)
        rendered = tmpl.render(**test_data)
        assert 'Test Documentation' in rendered
        assert 'test_module' in rendered
        assert 'TestClass' in rendered
        assert 'test_func' in rendered