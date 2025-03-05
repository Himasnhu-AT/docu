# API Reference

This page provides detailed documentation for Docu's public API.

## Core Functions

### `process_file`

```python
from docu import process_file

process_file(
    file_path: str,
    output_format: str = 'markdown',
    output_dir: Optional[str] = None,
    template_name: str = 'default',
    doc_style: str = 'google'
) -> str
```

Process a Python file and generate documentation.

**Parameters:**

- `file_path`: Path to the Python file
- `output_format`: Format of the output ('markdown' or 'html')
- `output_dir`: Directory to save the output file (if None, returns as string)
- `template_name`: Name of the template to use for HTML output
- `doc_style`: Documentation style to parse ('google', 'numpy', or 'sphinx')

**Returns:**

- If `output_dir` is provided: Path to the generated file
- If `output_dir` is None: Generated documentation content as a string

**Example:**

```python
# Generate HTML and save to file
output_path = process_file('my_file.py', output_format='html', output_dir='docs')
print(f"Documentation saved to: {output_path}")

# Generate markdown and get content as string
markdown_content = process_file('my_file.py', output_format='markdown')
print(markdown_content)
```

## Data Models

### `DocItem`

```python
from docu import DocItem

DocItem(
    name: str,
    doc: str,
    item_type: str,
    lineno: int,
    parent: Optional[str] = None,
    args: List[ArgumentInfo] = None,
    return_type: Optional[str] = None,
    fields: Dict[str, str] = None,
    methods: List['DocItem'] = None
)
```

Represents a documented item in the Python code.

**Fields:**

- `name`: Name of the item
- `doc`: Documentation string
- `item_type`: Type of the item ('class', 'function', 'method', 'module', etc.)
- `lineno`: Line number in the source file
- `parent`: Parent item name (for methods, this is the class name)
- `args`: List of argument information
- `return_type`: Return type annotation as a string
- `fields`: For classes, mapping of field name to type
- `methods`: For classes, list of method DocItems

### `ArgumentInfo`

```python
from docu import ArgumentInfo

ArgumentInfo(
    name: str,
    type_hint: Optional[str] = None,
    default: Optional[str] = None
)
```

Information about a function/method argument.

**Fields:**

- `name`: Name of the argument
- `type_hint`: Type hint as a string
- `default`: Default value as a string

## Template Management

### `TemplateManager`

```python
from docu import TemplateManager

template_manager = TemplateManager(templates_dir: str = None)
```

Template manager for documentation generation.

**Methods:**

#### `list_templates`

```python
template_manager.list_templates() -> List[Dict[str, str]]
```

List all available templates with their descriptions.

**Returns:**

- List of dictionaries containing template info (name, description)

#### `get_template`

```python
template_manager.get_template(name: str = 'default') -> Template
```

Get a template by name.

**Parameters:**

- `name`: Name of the template to load

**Returns:**

- Jinja2 Template object

**Raises:**

- `ValueError`: If template is not found

## Parser Functions

### `get_parser`

```python
from docu import get_parser

parser = get_parser(style: str = 'google')
```

Get a documentation style parser.

**Parameters:**

- `style`: Documentation style ('google', 'numpy', or 'sphinx')

**Returns:**

- DocStyleParser instance

**Raises:**

- `ValueError`: If style is not supported
