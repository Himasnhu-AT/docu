# Contributing to Docu

Thank you for considering contributing to Docu! This document provides an overview of the contribution workflow and guidelines.

## Ways to Contribute

There are many ways to contribute to Docu:

- Reporting bugs
- Suggesting new features
- Improving documentation
- Writing code
- Helping others in issues

## Development Environment Setup

1. Fork the repository on GitHub
2. Clone your fork locally

```bash
git clone https://github.com/Himasnhu-AT/docu.git
cd docu
```

3. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install development dependencies

```bash
pip install -e ".[dev]"
```

## Project Structure

- `docu/`: Main package directory
  - `__init__.py`: Package initialization
  - `cli.py`: Command-line interface
  - `docgen.py`: Core documentation generation
  - `parsers.py`: Python file parsing
  - `models.py`: Data models
  - `templates/`: HTML templates

## Running Tests

```bash
pytest
```

## Building Documentation

```bash
cd doc
npm run build
```

For more details, see the sections on [Code Style](./code-style) and [Pull Requests](./pull-requests).
