"""Document generation functionality."""

import os
from typing import Dict, List

from .models import DocItem
from .template_manager import TemplateManager
from .doc_parsers import get_parser

try:
    import markdown
    from markdown.extensions.tables import TableExtension
    from markdown.extensions.fenced_code import FencedCodeExtension
except ImportError:
    raise ImportError(
        "markdown package is required. Install it with: pip install markdown"
    )


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