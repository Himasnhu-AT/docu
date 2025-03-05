"""
Core documentation generation functionality.

This module contains the logic for parsing Python files and extracting
documentation from #/ comments, similar to Rust's cargo doc.
"""

import os
from typing import Optional

from .parsers import parse_python_file
from .generators import generate_markdown_docs, generate_html_docs


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