"""
docu - Generate documentation from Python files using #/ comments.
"""

from .docgen import process_file
from .models import DocItem, ArgumentInfo
from .doc_parsers import get_parser
from .template_manager import TemplateManager

__version__ = '0.1.0'

__all__ = [
    'process_file',
    'DocItem',
    'ArgumentInfo',
    'get_parser',
    'TemplateManager',
]
