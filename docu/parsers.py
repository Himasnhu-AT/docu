"""Core parsing functionality for Python files."""

import os
import ast
from typing import Dict, List, Optional, Tuple, Set

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
    
    # Dictionary to map AST nodes to their line ranges
    node_line_ranges = {}
    
    # First pass: identify all AST nodes and their line ranges
    for node in ast.walk(tree):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and hasattr(node, 'lineno'):
            # Get the end line number if available (Python 3.8+), otherwise compute it
            end_lineno = getattr(node, 'end_lineno', None)
            if end_lineno is None:
                # Estimate end line by finding the last line of the node's body
                end_lineno = node.lineno
                for child in ast.walk(node):
                    if hasattr(child, 'lineno'):
                        end_lineno = max(end_lineno, getattr(child, 'lineno', 0))
            
            node_line_ranges[node] = (node.lineno, end_lineno)
    
    # Identify the top-level nodes sorted by their position in the file
    top_level_nodes = [
        node for node in ast.iter_child_nodes(tree)
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    top_level_nodes.sort(key=lambda x: x.lineno)
    
    # Identify module-level comments (those before any top-level node)
    module_doc_lines = []
    used_doc_lines = set()
    
    # If there are top-level nodes, consider comments before the first one as module-level
    if top_level_nodes:
        first_node_line = top_level_nodes[0].lineno
        for line_no, comment in doc_comments:
            if line_no < first_node_line:
                # No blank line between module comments and first node - check for proximity
                if first_node_line - line_no > 3:  # Allow a reasonable gap
                    module_doc_lines.append(comment)
                    used_doc_lines.add(line_no)
    else:
        # No top-level nodes, all comments are module-level
        for line_no, comment in doc_comments:
            module_doc_lines.append(comment)
            used_doc_lines.add(line_no)
    
    # Create module documentation item if module docs exist
    module_name = os.path.basename(file_path).replace('.py', '')
    if module_doc_lines:
        doc_items[module_name] = DocItem(
            name=module_name,
            doc='\n'.join(module_doc_lines),
            item_type='module',
            lineno=1,
        )
    
    # Track class methods to attach them later
    class_methods = {}
    
    # Extract class and function documentation
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            # Find the closest preceding comments that haven't been used yet
            item_docs: List[str] = []
            
            # Start from the line above the node and go backwards
            for line_no in range(node.lineno - 1, max(0, node.lineno - 20), -1):
                if line_no in doc_lines and line_no not in used_doc_lines:
                    # Check if this line is a blank line or marks a break in comments
                    if line_no + 1 not in doc_lines and line_no != node.lineno - 1:
                        break
                    
                    item_docs.insert(0, doc_lines[line_no])
                    used_doc_lines.add(line_no)
                elif line_no not in doc_lines:
                    # Stop if we hit a non-documented line (except for blank lines)
                    with open(file_path, 'r') as f:
                        lines = f.readlines()
                    if line_no < len(lines) and lines[line_no].strip():
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