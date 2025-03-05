"""Data models for documentation generation."""

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class ArgumentInfo:
    """Information about a function/method argument."""
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
    methods: List['DocItem'] = None  # For classes, list of method DocItems

    def __post_init__(self):
        if self.args is None:
            self.args = []
        if self.fields is None:
            self.fields = {}
        if self.methods is None:
            self.methods = []
