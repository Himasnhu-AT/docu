---
layout: home
hero:
  name: Docu
  text: Python Documentation Generator
  tagline: Generate documentation from special #/ comment lines
  actions:
    - theme: brand
      text: Get Started
      link: /developers/getting-started
    - theme: alt
      text: View on GitHub
      link: https://github.com/Himasnhu-AT/docu
features:
  - title: Special #/ Comments
    details: Extract documentation from special #/ comment lines in your Python code
  - title: Multiple Output Formats
    details: Generate documentation in markdown or HTML with customizable templates
  - title: Support for Multiple Doc Styles
    details: Parse Google, NumPy, or Sphinx documentation styles
---

# Docu Documentation

Docu is a documentation generator for Python code that extracts documentation from special `#/` comment lines. It provides a straightforward way to document your Python code while keeping the documentation close to the code it describes.

## Key Features

- **Extract Documentation from Comments**: Docu extracts documentation from special `#/` comment lines in your Python code
- **Multiple Output Formats**: Generate documentation in markdown or HTML formats
- **Template System**: Customize the output using different HTML templates
- **Support for Multiple Doc Styles**: Parse documentation in Google, NumPy, or Sphinx styles
- **AST-based Analysis**: Accurately extracts function signatures, types, and return values

## Quick Example

```python
#/ MyClass - A simple example class
class MyClass:
    #/ Initialize the class with a name
    def __init__(self, name: str):
        self.name = name

    #/ Return a greeting using the name
    def greet(self) -> str:
        return f"Hello, {self.name}!"
```

Generate documentation with:

```bash
python -m docu example.py --format html --output-dir docs
```
