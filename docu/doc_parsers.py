"""Documentation style parsers for docu."""
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

@dataclass
class DocPart:
    """Represents a part of parsed documentation."""
    name: str
    content: str
    type: Optional[str] = None

class DocStyleParser:
    """Base class for documentation style parsers."""
    def parse(self, docstring: str) -> Dict[str, str]:
        """Parse a docstring into structured parts.
        
        Args:
            docstring: Raw docstring to parse
            
        Returns:
            Dictionary containing parsed documentation parts
        """
        raise NotImplementedError

class GoogleStyleParser(DocStyleParser):
    """Parser for Google style docstrings."""
    
    def parse(self, docstring: str) -> Dict[str, str]:
        if not docstring:
            return {}
            
        sections = {'description': '', 'args': [], 'returns': '', 'raises': []}
        current_section = 'description'
        indent_level = None
        description_lines = []
        current_indent = 0
        
        lines = [line.rstrip() for line in docstring.splitlines()]
        
        # Find the first non-empty line to determine base indentation
        for line in lines:
            if line.strip():
                indent_level = len(line) - len(line.lstrip())
                break
        
        if indent_level is None:
            return sections
            
        # Process lines with proper indentation handling
        for line in lines:
            stripped = line.strip()
            if not stripped:
                if current_section == 'description':
                    description_lines.append('')
                continue
                
            line_indent = len(line) - len(line.lstrip())
            # Remove base indentation
            if line_indent > indent_level:
                line = line[indent_level:]
                current_indent = line_indent - indent_level
            else:
                line = line.lstrip()
                current_indent = 0
            
            # Check for section headers
            lower_stripped = stripped.lower()
            if lower_stripped == 'args:':
                current_section = 'args'
                continue
            elif lower_stripped == 'returns:':
                current_section = 'returns'
                continue
            elif lower_stripped == 'raises:':
                current_section = 'raises'
                continue
                
            # Add content to current section
            if current_section == 'description':
                description_lines.append(line)
            elif current_section == 'args':
                # Only capture lines with additional indentation (arg descriptions)
                if current_indent > 0:
                    sections['args'].append(stripped)
            elif current_section == 'returns':
                if current_indent > 0:
                    sections['returns'] += stripped + '\n'
            elif current_section == 'raises':
                if current_indent > 0:
                    sections['raises'].append(stripped)
        
        sections['description'] = '\n'.join(description_lines).strip()
        sections['returns'] = sections['returns'].strip()
        return sections

class NumpyStyleParser(DocStyleParser):
    """Parser for NumPy style docstrings."""
    
    def parse(self, docstring: str) -> Dict[str, str]:
        if not docstring:
            return {}
            
        sections = {'description': '', 'parameters': [], 'returns': '', 'raises': []}
        current_section = 'description'
        lines = docstring.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Check for section headers
            if line.lower() == 'parameters':
                current_section = 'parameters'
                continue
            elif line.lower() == 'returns':
                current_section = 'returns'
                continue
            elif line.lower() == 'raises':
                current_section = 'raises'
                continue
                
            # Add content to current section
            if current_section == 'description':
                sections['description'] += line + '\n'
            elif current_section in ('parameters', 'raises') and line:
                if ':' in line:
                    sections[current_section].append(line.strip())
            elif current_section == 'returns' and line:
                sections['returns'] += line + '\n'
                
        return sections

class SphinxStyleParser(DocStyleParser):
    """Parser for Sphinx style docstrings."""
    
    def parse(self, docstring: str) -> Dict[str, str]:
        if not docstring:
            return {}
            
        sections = {'description': '', 'params': [], 'returns': '', 'raises': []}
        current_section = 'description'
        lines = docstring.split('\n')
        
        for line in lines:
            line = line.strip()
            
            # Check for Sphinx directives
            if line.startswith(':param'):
                current_section = 'params'
                sections['params'].append(line[6:].strip())
            elif line.startswith(':returns:'):
                current_section = 'returns'
                sections['returns'] += line[9:].strip() + '\n'
            elif line.startswith(':raises:'):
                current_section = 'raises'
                sections['raises'].append(line[8:].strip())
            elif current_section == 'description':
                sections['description'] += line + '\n'
                
        return sections

def get_parser(style: str = 'google') -> DocStyleParser:
    """Get a documentation style parser.
    
    Args:
        style: Documentation style ('google', 'numpy', or 'sphinx')
        
    Returns:
        DocStyleParser instance
        
    Raises:
        ValueError: If style is not supported
    """
    parsers = {
        'google': GoogleStyleParser,
        'numpy': NumpyStyleParser,
        'sphinx': SphinxStyleParser
    }
    
    if style not in parsers:
        raise ValueError(f"Unsupported documentation style: {style}")
        
    return parsers[style]()