"""Core parsing functionality for Python files."""

import os
import ast
from typing import Dict, List, Optional, Tuple

from .ast_utils import get_type_str
from .models import ArgumentInfo, DocItem


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