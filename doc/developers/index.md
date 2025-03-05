# Developer Guide

Welcome to the Docu developer guide! This section provides information for developers who want to use Docu as a library in their own projects or understand its internals.

## Overview

Docu is a Python documentation generator that extracts documentation from special `#/` comment lines in Python code. It's designed to be:

- **Simple to use**: Clear and straightforward API
- **Flexible**: Support for different documentation styles and output formats
- **Extensible**: Easy to add new templates and parsers

## Installation

Install Docu using pip:

```bash
pip install docu
```

## Basic Usage

Here's a simple example of using Docu as a library:

```python
from docu import process_file

# Generate HTML documentation
html_output = process_file(
    'my_file.py',
    output_format='html',
    output_dir='docs',
    template_name='default',
    doc_style='google'
)

print(f"Documentation saved to: {html_output}")
```

## Core Modules

- **docgen**: Main documentation generation logic
- **parsers**: Python file parsing functionality
- **models**: Data models for documentation items
- **generators**: Output generation in different formats
- **template_manager**: HTML template handling

For more details, check out the [Getting Started](./getting-started) guide and the [API Reference](./api-reference).
