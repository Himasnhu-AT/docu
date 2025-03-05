"""
Core documentation generation functionality.

This module contains the logic for parsing Python files and extracting
documentation from #/ comments, similar to Rust's cargo doc.
"""

import os
import ast
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

try:
    import markdown
    from markdown.extensions.tables import TableExtension
    from markdown.extensions.fenced_code import FencedCodeExtension
except ImportError:
    raise ImportError(
        "markdown package is required. Install it with: pip install markdown"
    )


@dataclass
class DocItem:
    """Represents a documented item in the Python code."""
    name: str
    doc: str
    item_type: str  # 'class', 'function', 'method', 'module', etc.
    lineno: int
    parent: Optional[str] = None


def extract_doc_comments(file_path: str) -> List[Tuple[int, str]]:
    """Extract all #/ comments from a Python file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of (line_number, comment_text) tuples
    """
    doc_comments: List[Tuple[int, str]] = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if line.startswith('#/'):
                comment = line[2:].strip()
                doc_comments.append((i, comment))
    
    return doc_comments


def parse_python_file(file_path: str) -> Dict[str, DocItem]:
    """Parse a Python file and extract documentation for code elements.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        Dictionary of DocItem objects keyed by their full names
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract all #/ comments
    doc_comments = extract_doc_comments(file_path)
    doc_lines = {line_no: comment for line_no, comment in doc_comments}
    
    # Parse the Python file
    tree = ast.parse(content, filename=file_path)
    
    # Dictionary to store documentation items
    doc_items: Dict[str, DocItem] = {}
    
    # Extract module-level documentation
    module_name = os.path.basename(file_path).replace('.py', '')
    module_doc: List[str] = []
    
    # Find module-level documentation (comments at the top of the file)
    for line_no, comment in doc_comments:
        if any(
            isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Assign))
            for node in ast.walk(tree)
            if hasattr(node, 'lineno') and node.lineno > line_no
        ):
            module_doc.append(comment)
        else:
            break
    
    if module_doc:
        doc_items[module_name] = DocItem(
            name=module_name,
            doc='\n'.join(module_doc),
            item_type='module',
            lineno=1,
        )
    
    # Extract class and function documentation
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            # Check if there are #/ comments before this node
            item_docs: List[str] = []
            for line_no in range(node.lineno - 1, 0, -1):
                if line_no in doc_lines:
                    item_docs.insert(0, doc_lines[line_no])
                else:
                    # Stop if we hit a non-documented line
                    break
            
            if item_docs:
                parent = None
                for parent_node in ast.walk(tree):
                    if (
                        isinstance(parent_node, ast.ClassDef)
                        and parent_node.lineno < node.lineno
                        and node in parent_node.body
                    ):
                        parent = parent_node.name
                        break
                
                item_type = 'class' if isinstance(node, ast.ClassDef) else 'function'
                if parent and item_type == 'function':
                    item_type = 'method'
                
                full_name = f"{parent}.{node.name}" if parent else node.name
                doc_items[full_name] = DocItem(
                    name=node.name,
                    doc='\n'.join(item_docs),
                    item_type=item_type,
                    lineno=node.lineno,
                    parent=parent
                )
    
    return doc_items


def generate_markdown_docs(doc_items: Dict[str, DocItem]) -> str:
    """Generate markdown documentation from parsed docitems.
    
    Args:
        doc_items: Dictionary of DocItem objects
        
    Returns:
        Markdown formatted documentation
    """
    md_content = []
    
    # Module documentation first
    module_items = [item for item in doc_items.values() if item.item_type == 'module']
    if module_items:
        module = module_items[0]
        md_content.append(f"# Module {module.name}")
        md_content.append(module.doc)
        md_content.append("")
    
    # Classes
    classes = [item for item in doc_items.values() if item.item_type == 'class']
    if classes:
        md_content.append("## Classes")
        for cls in sorted(classes, key=lambda x: x.name):
            md_content.append(f"### {cls.name}")
            md_content.append(cls.doc)
            md_content.append("")
            
            # Add methods of this class
            methods = [
                item for item in doc_items.values()
                if item.item_type == 'method' and item.parent == cls.name
            ]
            if methods:
                for method in sorted(methods, key=lambda x: x.name):
                    md_content.append(f"#### {method.name}")
                    md_content.append(method.doc)
                    md_content.append("")
    
    # Functions (not methods)
    functions = [
        item for item in doc_items.values()
        if item.item_type == 'function' and not item.parent
    ]
    if functions:
        md_content.append("## Functions")
        for func in sorted(functions, key=lambda x: x.name):
            md_content.append(f"### {func.name}")
            md_content.append(func.doc)
            md_content.append("")
    
    return '\n'.join(md_content)


def generate_html_docs(doc_items: Dict[str, DocItem]) -> str:
    """Generate HTML documentation from parsed docitems.
    
    Args:
        doc_items: Dictionary of DocItem objects
        
    Returns:
        HTML formatted documentation
    """
    md_content = generate_markdown_docs(doc_items)
    html_content = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Python Documentation</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", 
                Roboto, Helvetica, Arial, sans-serif;
                line-height: 1.6;
                padding: 20px;
                max-width: 800px;
                margin: 0 auto;
            }}
            h1 {{
                border-bottom: 1px solid #eaecef;
                padding-bottom: 0.3em;
            }}
            h2 {{
                border-bottom: 1px solid #eaecef;
                padding-bottom: 0.3em;
                margin-top: 24px;
                margin-bottom: 16px;
            }}
            code {{
                font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, 
                monospace;
                background-color: rgba(27,31,35,0.05);
                padding: 0.2em 0.4em;
                border-radius: 3px;
            }}
            pre {{
                background-color: #f6f8fa;
                border-radius: 3px;
                padding: 16px;
                overflow: auto;
            }}
            pre code {{
                background-color: transparent;
                padding: 0;
            }}
        </style>
    </head>
    <body>
        {html_content}
    </body>
    </html>
    """
    
    return html_template


def process_file(
    file_path: str,
    output_format: str = 'markdown',
    output_dir: Optional[str] = None
) -> str:
    """Process a Python file and generate documentation.
    
    Args:
        file_path: Path to the Python file
        output_format: Format of the output ('markdown' or 'html')
        output_dir: Directory to save the output file (if None, returns as string)
        
    Returns:
        Generated documentation content
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    doc_items = parse_python_file(file_path)
    
    if output_format == 'markdown':
        content = generate_markdown_docs(doc_items)
        extension = 'md'
    else:  # html
        content = generate_html_docs(doc_items)
        extension = 'html'
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        base_filename = os.path.basename(file_path).replace('.py', f'.{extension}')
        output_path = os.path.join(output_dir, base_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path
    
    return content