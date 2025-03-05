# Code Style Guidelines

Docu follows a consistent code style to make the codebase more maintainable. Please follow these guidelines when contributing.

## Python Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style
- Use 4 spaces for indentation
- Maximum line length of 88 characters (compatible with Black)
- Use type hints for function parameters and return types
- Use docstrings for all public modules, classes, and functions

## Docstrings

Docu uses Google-style docstrings. For example:

```python
def function(arg1: str, arg2: int = 42) -> bool:
    """Short description of the function.

    Longer description that can span multiple lines.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of the return value

    Raises:
        ValueError: If something goes wrong
    """
```

## Code Quality Tools

We use the following tools to maintain code quality:

- **Black**: For code formatting
- **isort**: For import sorting
- **Flake8**: For code linting
- **MyPy**: For type checking

You can run all these tools with the following commands:

```bash
black docu tests
isort docu tests
flake8 docu tests
mypy docu
```

## HTML/CSS Style (Templates)

For HTML templates:

- Use 4 spaces for indentation
- Use double quotes for attributes
- Keep template logic minimal and focused on presentation

## JavaScript Style

- Use 2 spaces for indentation
- Follow [StandardJS](https://standardjs.com/) style
- Prefer const over let when a variable is not reassigned
