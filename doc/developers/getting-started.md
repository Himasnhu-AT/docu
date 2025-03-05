# Getting Started with Docu

This guide will help you get started with using Docu in your project, both as a command-line tool and as a library.

## Installation

Install Docu using pip:

```bash
pip install docu
```

## Using Docu as a Command-Line Tool

### Basic Usage

```bash
python -m docu your_file.py --output-dir docs
```

This will generate HTML documentation for `your_file.py` and save it in the `docs` directory.

### Command-Line Options

- `--format, -f`: Output format (`markdown` or `html`, default: `html`)
- `--output-dir, -o`: Directory to save the generated documentation
- `--template, -t`: HTML template to use (default: `default`)
- `--doc-style, -s`: Documentation style to parse (`google`, `numpy`, or `sphinx`, default: `google`)
- `--verbose, -v`: Enable verbose output

### Examples

Generate markdown documentation:

```bash
python -m docu your_file.py --format markdown --output-dir docs
```

Use a specific template:

```bash
python -m docu your_file.py --template modern --output-dir docs
```

Parse NumPy-style docstrings:

```bash
python -m docu your_file.py --doc-style numpy --output-dir docs
```

## Using Docu as a Library

### Basic Example

```python
from docu import process_file

# Generate HTML documentation
output_path = process_file(
    'your_file.py',
    output_format='html',
    output_dir='docs',
    template_name='default',
    doc_style='google'
)

print(f"Documentation saved to: {output_path}")
```

### Working with Templates

```python
from docu import TemplateManager

# List available templates
template_manager = TemplateManager()
templates = template_manager.list_templates()
for template in templates:
    print(f"{template['name']}: {template['description']}")

# Get a specific template
template = template_manager.get_template('modern')
```

### Custom Processing

```python
from docu import parse_python_file, generate_markdown_docs

# Parse Python file
doc_items = parse_python_file('your_file.py')

# Generate markdown documentation
markdown_content = generate_markdown_docs(doc_items)

# Save to file
with open('docs/your_file.md', 'w') as f:
    f.write(markdown_content)
```

## Next Steps

- Check out the [API Reference](./api-reference) for detailed information on Docu's API
- Learn about [Code Organization](../architecture/code-organization) to understand how Docu works
- Read the [Templates Guide](../architecture/templates) to create custom templates
