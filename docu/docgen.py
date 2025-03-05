"""
Core documentation generation functionality.

This module contains the logic for parsing Python files and extracting
documentation from #/ comments, similar to Rust's cargo doc.
"""

import os
import ast
import inspect
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union, Any
from .template_manager import TemplateManager
from .doc_parsers import get_parser, DocStyleParser

try:
    import markdown
    from markdown.extensions.tables import TableExtension
    from markdown.extensions.fenced_code import FencedCodeExtension
except ImportError:
    raise ImportError(
        "markdown package is required. Install it with: pip install markdown"
    )


@dataclass
class ArgumentInfo:
    name: str
    type_hint: Optional[str] = None
    default: Optional[str] = None


@dataclass
class DocItem:
    """Represents a documented item in the Python code."""
    name: str
    doc: str
    item_type: str  # 'class', 'function', 'method', 'module', etc.
    lineno: int
    parent: Optional[str] = None
    args: List[ArgumentInfo] = None
    return_type: Optional[str] = None
    fields: Dict[str, str] = None  # For classes, mapping of field name to type

    def __post_init__(self):
        if self.args is None:
            self.args = []
        if self.fields is None:
            self.fields = {}


def get_type_str(node: ast.AST) -> str:
    """Convert AST type annotation to string representation."""
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Subscript):
        value = get_type_str(node.value)
        slice_val = get_type_str(node.slice)
        return f"{value}[{slice_val}]"
    elif isinstance(node, ast.Attribute):
        return f"{get_type_str(node.value)}.{node.attr}"
    elif isinstance(node, ast.Constant):
        return str(node.value)
    elif isinstance(node, ast.List):
        elts = [get_type_str(elt) for elt in node.elts]
        return f"[{', '.join(elts)}]"
    elif isinstance(node, ast.Tuple):
        elts = [get_type_str(elt) for elt in node.elts]
        return f"({', '.join(elts)})"
    return "Any"


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
    
    # Only include module if it has documentation
    if module_doc:
        doc_items[module_name] = DocItem(
            name=module_name,
            doc='\n'.join(module_doc),
            item_type='module',
            lineno=1,
        )
    
    # Track class methods to attach them later
    class_methods = {}
    
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
            
            # Extract argument information
            args = []
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for arg in node.args.args:
                    if arg.arg == 'self':
                        continue
                    type_hint = None
                    if arg.annotation:
                        type_hint = get_type_str(arg.annotation)
                    args.append(ArgumentInfo(name=arg.arg, type_hint=type_hint))
            
            # Extract return type
            return_type = None
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.returns:
                return_type = get_type_str(node.returns)
            
            # Extract class fields
            fields = {}
            if isinstance(node, ast.ClassDef):
                for child in node.body:
                    if isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
                        fields[child.target.id] = get_type_str(child.annotation)
            
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
            
            # Store methods separately to attach to classes later
            if item_type == 'method':
                if parent not in class_methods:
                    class_methods[parent] = []
                class_methods[parent].append(doc_item)
                continue  # Don't add methods to doc_items directly
            
            full_name = f"{parent}.{node.name}" if parent else node.name
            doc_items[full_name] = doc_item
    
    # Attach methods to their respective classes
    for class_name, methods in class_methods.items():
        if class_name in doc_items:
            doc_items[class_name].methods = sorted(methods, key=lambda x: x.lineno)
    
    return doc_items


def generate_markdown_docs(doc_items: Dict[str, DocItem]) -> str:
    """Generate markdown documentation from parsed docitems.
    
    Args:
        doc_items: Dictionary of DocItem objects
        
    Returns:
        Markdown formatted documentation
    """
    md_content = []
    
    # Module documentation only if it exists
    module_items = [item for item in doc_items.values() if item.item_type == 'module']
    if module_items and module_items[0].doc:
        module = module_items[0]
        md_content.append(f"# Module {module.name}")
        md_content.append(module.doc)
        md_content.append("")
    
    # Classes
    classes = [item for item in doc_items.values() if item.item_type == 'class']
    if classes:
        if not md_content:  # Add module header if not already added
            md_content.append(f"# Module {os.path.basename(classes[0].name)}")
            md_content.append("")
        
        md_content.append("## Classes")
        for cls in sorted(classes, key=lambda x: x.name):
            md_content.append(f"\n### class {cls.name}")
            
            if cls.fields:
                md_content.append("\n#### Fields")
                for field_name, field_type in cls.fields.items():
                    md_content.append(f"- **{field_name}**: {field_type}")
            
            if cls.doc:
                md_content.append("\n" + cls.doc)
            
            # Add methods of this class
            methods = [
                item for item in doc_items.values()
                if item.item_type == 'method' and item.parent == cls.name
            ]
            if methods:
                md_content.append("\n#### Methods")
                for method in sorted(methods, key=lambda x: x.name):
                    md_content.append(f"\n##### {method.name}")
                    
                    # Show signature
                    args_str = ", ".join(
                        f"{arg.name}: {arg.type_hint if arg.type_hint else 'Any'}"
                        for arg in method.args
                    )
                    signature = f"```python\ndef {method.name}({args_str})"
                    if method.return_type:
                        signature += f" -> {method.return_type}"
                    signature += "\n```"
                    md_content.append(signature)
                    
                    if method.doc:
                        md_content.append(method.doc)
                    
                    if method.args:
                        md_content.append("**Arguments**")
                        for arg in method.args:
                            md_content.append(f"- {arg.name}: {arg.type_hint if arg.type_hint else 'Any'}")
                    
                    if method.return_type:
                        md_content.append(f"**Returns**\n- {method.return_type}")
            
            md_content.append("")
    
    # Functions (not methods)
    functions = [
        item for item in doc_items.values()
        if item.item_type == 'function' and not item.parent
    ]
    if functions:
        md_content.append("## Functions")
        for func in sorted(functions, key=lambda x: x.name):
            md_content.append(f"\n### {func.name}")
            
            # Show signature
            args_str = ", ".join(
                f"{arg.name}: {arg.type_hint if arg.type_hint else 'Any'}"
                for arg in func.args
            )
            signature = f"```python\ndef {func.name}({args_str})"
            if func.return_type:
                signature += f" -> {func.return_type}"
            signature += "\n```"
            md_content.append(signature)
            
            if func.doc:
                md_content.append(func.doc)
            
            if func.args:
                md_content.append("**Arguments**")
                for arg in func.args:
                    md_content.append(f"- {arg.name}: {arg.type_hint if arg.type_hint else 'Any'}")
            
            if func.return_type:
                md_content.append(f"**Returns**\n- {func.return_type}")
            
            md_content.append("")
    
    return '\n'.join(md_content)


def generate_html_docs(doc_items: Dict[str, DocItem], template_name: str = 'default', doc_style: str = 'google') -> str:
    """Generate HTML documentation from parsed docitems.
    
    Args:
        doc_items: Dictionary of DocItem objects
        template_name: Name of the template to use
        doc_style: Documentation style to parse ('google', 'numpy', or 'sphinx')
        
    Returns:
        HTML formatted documentation
    """
    # Get template manager and parser
    template_manager = TemplateManager()
    doc_parser = get_parser(doc_style)
    
    # Parse documentation with selected style
    parsed_docs = {}
    for name, item in doc_items.items():
        if item.doc:
            parsed_docs[name] = doc_parser.parse(item.doc)
    
    # Get template
    template = template_manager.get_template(template_name)
    
    # First, we need to process any class methods
    classes = [item for item in doc_items.values() if item.item_type == 'class']
    for class_item in classes:
        if hasattr(class_item, 'methods'):
            for method in class_item.methods:
                method_full_name = f"{class_item.name}.{method.name}"
                if method.doc:
                    parsed_docs[method_full_name] = doc_parser.parse(method.doc)
    
    # Prepare template data
    template_data = {
        'items': doc_items,
        'parsed_docs': parsed_docs,
        'module_items': [item for item in doc_items.values() if item.item_type == 'module'],
        'classes': classes,
        'functions': [item for item in doc_items.values() if item.item_type == 'function' and not item.parent],
    }
    
    # Render template
    return template.render(**template_data)


def process_file(
    file_path: str,
    output_format: str = 'markdown',
    output_dir: Optional[str] = None,
    template_name: str = 'default',
    doc_style: str = 'google'
) -> str:
    """Process a Python file and generate documentation.
    
    Args:
        file_path: Path to the Python file
        output_format: Format of the output ('markdown' or 'html')
        output_dir: Directory to save the output file (if None, returns as string)
        template_name: Name of the template to use for HTML output
        doc_style: Documentation style to parse ('google', 'numpy', or 'sphinx')
        
    Returns:
        Generated documentation content
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    doc_items = parse_python_file(file_path)
    
    if output_format == 'markdown':
        content = generate_markdown_docs(doc_items)
        extension = 'md'
        # For markdown, use original naming
        output_filename = os.path.basename(file_path).replace('.py', f'.{extension}')
    else:  # html
        content = generate_html_docs(doc_items, template_name, doc_style)
        extension = 'html'
        # For HTML, include template name in the filename
        base_name = os.path.basename(file_path).replace('.py', '')
        output_filename = f"{base_name}_{template_name}.{extension}"
    
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path
    
    return content