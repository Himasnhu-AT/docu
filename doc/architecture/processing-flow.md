# Processing Flow

This page describes the data flow through Docu, from Python file to documentation output.

## Overview

The documentation generation process in Docu follows these main steps:

1. **Input Processing**: Parse Python file and extract special comments
2. **Documentation Extraction**: Extract documentation from comments
3. **Code Analysis**: Analyze code structure using AST
4. **Documentation Processing**: Process documentation according to style
5. **Output Generation**: Generate documentation in the requested format

## Detailed Flow

```
┌────────────┐    ┌───────────────┐    ┌──────────────┐
│ Python File│───▶│  AST Parsing  │───▶│Comment Parser│
└────────────┘    └───────────────┘    └──────┬───────┘
                                              │
                                              ▼
┌──────────────┐    ┌────────────────┐    ┌──────────────┐
│Output Format │◀───│ Documentation  │◀───│ Doc Structure│
│ (MD/HTML)    │    │   Generator    │    │  Extraction  │
└──────────────┘    └────────────────┘    └──────────────┘
```

## Step-By-Step Explanation

### 1. File Reading and AST Parsing

```python
# In parsers.py
def parse_python_file(file_path: str) -> Dict[str, DocItem]:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Extract all #/ comments
    doc_comments = extract_doc_comments(file_path)

    # Parse the Python file using AST
    tree = ast.parse(content, filename=file_path)

    # Process the AST...
```

First, Docu reads the Python file and parses it using Python's built-in Abstract Syntax Tree (AST) module. This gives Docu a structured representation of the Python code that can be analyzed.

### 2. Comment Extraction

```python
# In parsers.py
def extract_doc_comments(file_path: str) -> List[Tuple[int, str]]:
    doc_comments: List[Tuple[int, str]] = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if line.startswith('#/'):
                comment = line[2:].strip()
                doc_comments.append((i, comment))

    return doc_comments
```

Docu identifies and extracts all lines that start with the special `#/` comment marker. These comments contain the documentation that will be processed.

### 3. Code Structure Analysis

While traversing the AST, Docu identifies:

- Classes
- Functions
- Methods
- Module-level documentation
- Type annotations
- Return types
- Class fields

It associates the special comments with these code elements based on their positions in the file.

### 4. Documentation Processing

```python
# In doc_parsers.py
class GoogleStyleParser(DocStyleParser):
    def parse(self, docstring: str) -> Dict[str, str]:
        # Process Google-style docstrings
        sections = {'description': '', 'args': [], 'returns': '', 'raises': []}
        # Parsing logic...
        return sections
```

The extracted documentation is processed according to the specified style (Google, NumPy, or Sphinx). This extracts structured information like argument descriptions, return value descriptions, and raised exceptions.

### 5. Documentation Structure Creation

```python
# In parsers.py
doc_item = DocItem(
    name=node.name,
    doc='\n'.join(item_docs) if item_docs else "",
    item_type=item_type,
    lineno=node.lineno,
    parent=parent,
    args=args,
    return_type=return_type,
    fields=fields
)
```

Docu creates a structured representation of the documentation using the `DocItem` class. This includes all the information about the code element and its documentation.

### 6. Output Generation

#### Markdown Generation

```python
# In generators.py
def generate_markdown_docs(doc_items: Dict[str, DocItem]) -> str:
    md_content = []
    # Generate markdown content from doc_items
    return '\n'.join(md_content)
```

For markdown output, Docu generates a structured markdown document from the `DocItem` objects.

#### HTML Generation

```python
# In generators.py
def generate_html_docs(doc_items: Dict[str, DocItem], template_name: str = 'default', doc_style: str = 'google') -> str:
    # Get template manager and parser
    template_manager = TemplateManager()
    template = template_manager.get_template(template_name)

    # Prepare template data
    template_data = {
        'items': doc_items,
        # Additional data...
    }

    # Render template
    return template.render(**template_data)
```

For HTML output, Docu prepares data for the template and then renders the selected HTML template with this data.

### 7. Output Handling

```python
# In docgen.py
if output_dir:
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, output_filename)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return output_path

return content
```

Finally, Docu either saves the generated documentation to a file or returns it as a string, depending on whether an output directory was specified.

## Error Handling

Throughout the process, Docu includes error handling to deal with:

- Missing files
- Invalid Python syntax
- Unsupported documentation styles
- Missing templates
- File writing errors

Error messages are propagated to the user either through exceptions or through the CLI output.
