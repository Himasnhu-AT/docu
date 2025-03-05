# Code Organization

This page describes how the Docu codebase is organized, the responsibilities of each module, and how they interact.

## Package Structure

```
docu/
├── __init__.py          # Package initialization and exports
├── __main__.py          # Entry point for running as a module
├── ast_utils.py         # AST utility functions
├── cli.py               # Command-line interface
├── doc_parsers.py       # Parsers for different doc styles
├── docgen.py            # Core documentation generation
├── generators.py        # Output generators (markdown, HTML)
├── models.py            # Data models
├── parsers.py           # Python file parsing
├── template_manager.py  # HTML template management
└── templates/           # HTML templates
    ├── default.html     # Default template
    ├── minimal.html     # Minimal template
    ├── modern.html      # Modern template with dark mode
    ├── rtd.html         # ReadTheDocs-inspired template
    └── schema.json      # Template schema definition
```

## Module Responsibilities

### `__init__.py`

- Exports public API
- Defines version information

### `__main__.py`

- Entry point for running Docu as a module
- Calls the main CLI function

### `ast_utils.py`

- Utility functions for working with Python's Abstract Syntax Tree (AST)
- Converts AST type annotations to string representations

### `cli.py`

- Command-line interface implementation
- Argument parsing and command execution
- Main entry point for CLI usage

### `doc_parsers.py`

- Parsers for different documentation styles
- Supports Google, NumPy, and Sphinx styles
- Extracts structured information from docstrings

### `docgen.py`

- Core documentation generation functionality
- Orchestrates the documentation process
- Main entry point for library usage

### `generators.py`

- Output generation in different formats
- Markdown generator
- HTML generator with template support

### `models.py`

- Data models for documentation items
- Defines the structure of parsed documentation
- Used throughout the codebase for consistent data handling

### `parsers.py`

- Python file parsing functionality
- Extracts documentation from special `#/` comments
- Analyzes code structure using AST

### `template_manager.py`

- HTML template management
- Lists and loads templates
- Validates template configurations

### `templates/`

- HTML templates for documentation output
- Each template has an HTML file and a JSON configuration
- Schema definition for template validation

## Dependency Graph

The following diagram shows the dependency relationships between the main modules:

```
           ┌────────────┐
           │ __main__.py│
           └─────┬──────┘
                 │
                 ▼
           ┌────────────┐
           │   cli.py   │
           └─────┬──────┘
                 │
                 ▼
           ┌────────────┐
           │  docgen.py │
           └─────┬──────┘
                 │
      ┌──────────┴──────────┐
      │                     │
      ▼                     ▼
┌───────────┐       ┌─────────────┐
│ parsers.py│       │generators.py│
└─────┬─────┘       └──────┬──────┘
      │                    │
      ▼                    ▼
┌───────────┐      ┌──────────────────┐
│models.py  │      │template_manager.py│
└───────────┘      └──────────────────┘
```

## Key Classes and Functions

### Main Entry Points

- `docu.process_file()`: Main library entry point
- `docu.cli.main()`: Main CLI entry point

### Core Classes

- `docu.models.DocItem`: Represents a documented item
- `docu.models.ArgumentInfo`: Information about function arguments
- `docu.doc_parsers.DocStyleParser`: Base class for doc style parsers
- `docu.template_manager.TemplateManager`: Manages HTML templates

### Key Functions

- `docu.parsers.parse_python_file()`: Parse a Python file and extract documentation
- `docu.generators.generate_markdown_docs()`: Generate markdown documentation
- `docu.generators.generate_html_docs()`: Generate HTML documentation
