# Docu

A Python command-line tool to generate documentation from Python files using `#/` comments, inspired by Rust's `cargo doc` command.

## Features

- Extracts documentation from special `#/` comment lines in Python code
- Supports documentation for modules, classes, and functions
- Generates both Markdown and HTML documentation formats
- Clean and attractive output with proper formatting

## Installation

### From PyPI (Not yet published)

```bash
pip install docu
```

### From Source

```bash
# Clone the repository
git clone https://github.com/Himasnhu-AT/docu.git
cd docu

# Use the setup script
./scripts/setup.sh
# OR install manually
python -m venv venv
source venv/bin/activate
pip install -e .
```

## Usage

Basic usage:

```bash
docu /path/to/your/python_file.py
```

Options:

```
--format, -f [markdown|html]  Output format for the documentation (default: html)
--output-dir, -o PATH         Directory to save the generated documentation
--verbose, -v                 Enable verbose output
```

Examples:

```bash
# Generate HTML documentation and save it to the docs directory
docu my_code.py --output-dir docs

# Generate Markdown documentation
docu my_code.py --format markdown

# Process a file with verbose output
docu my_code.py --verbose
```

## Comment Format

The tool processes special comments that start with `#/`. Here's how to use them:

```python
#/ This is a module-level documentation comment.
#/ It will be included in the module documentation.

#/ This is a class documentation comment.
class MyClass:
    #/ This documents the __init__ method.
    def __init__(self, value):
        self.value = value
        
    #/ This documents another method.
    #/ You can use multiple lines.
    #/ 
    #/ Parameters:
    #/ - param1: Description of parameter 1
    def my_method(self, param1):
        pass

#/ This documents a function.
def my_function():
    pass
```

## Development

### Setting up the development environment

```bash
./scripts/setup.sh
```

### Running tests

```bash
./scripts/test.sh
```

### Building the package

```bash
./scripts/build.sh
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the BSD 3-Clause License - see the LICENSE file for details.