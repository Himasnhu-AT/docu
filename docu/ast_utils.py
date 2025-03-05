"""AST utilities for parsing Python code."""

import ast
from typing import Optional

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