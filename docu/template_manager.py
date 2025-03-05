"""Template manager for docu."""
from pathlib import Path
import json
from typing import Dict, Any, Optional, List
from jinja2 import Environment, FileSystemLoader, Template

class TemplateManager:
    """Template manager for documentation generation.

    Available templates:
    - default: Clean, responsive HTML template with proper code formatting
    - minimal: Lightweight template with basic styling
    - modern: Modern template with dark/light mode support
    - rtd: ReadTheDocs-inspired template
    """

    def __init__(self, templates_dir: str = None):
        """Initialize template manager.

        Args:
            templates_dir: Directory containing templates. If None, uses default templates directory.
        """
        if templates_dir is None:
            templates_dir = Path(__file__).parent / 'templates'
        self.templates_dir = Path(templates_dir)
        self.env = Environment(loader=FileSystemLoader(str(self.templates_dir)))
        self.schema = self._load_schema()

    def _load_schema(self) -> Dict[str, Any]:
        """Load template schema from JSON file."""
        schema_path = self.templates_dir / 'schema.json'
        with open(schema_path) as f:
            return json.load(f)

    def list_templates(self) -> List[Dict[str, str]]:
        """List all available templates with their descriptions.

        Returns:
            List of dictionaries containing template info (name, description)
        """
        templates = []
        for template_file in self.templates_dir.glob('*.html'):
            name = template_file.stem
            try:
                with open(self.templates_dir / f'{name}.json', 'r') as f:
                    config = json.load(f)
                    templates.append({
                        'name': name,
                        'description': config.get('description', ''),
                        'doc_style': config.get('docstyle', 'google')
                    })
            except FileNotFoundError:
                if name == 'default':
                    templates.append({
                        'name': name,
                        'description': 'Default template with clean, responsive design',
                        'doc_style': 'google'
                    })
        return templates

    def get_template(self, name: str = 'default') -> Template:
        """Get template by name.

        Args:
            name: Name of the template to load

        Returns:
            Jinja2 Template object

        Raises:
            ValueError: If template is not found
        """
        if not (self.templates_dir / f'{name}.html').exists():
            available = [t['name'] for t in self.list_templates()]
            templates_str = '\n- '.join([''] + available)
            raise ValueError(
                f"Template '{name}' not found. Available templates:{templates_str}"
            )
        return self.env.get_template(f'{name}.html')

    def validate_template(self, template_data: Dict[str, Any]) -> bool:
        """Validate template data against schema.

        Args:
            template_data: Template data to validate

        Returns:
            True if valid, False otherwise

        Raises:
            ValueError: If validation fails
        """
        required = set(self.schema['required'])
        if not all(key in template_data for key in required):
            missing = required - set(template_data.keys())
            raise ValueError(f"Missing required fields: {', '.join(missing)}")

        for key, value in template_data.items():
            if key not in self.schema['properties']:
                raise ValueError(f"Unknown field: {key}")

            prop = self.schema['properties'][key]
            if key == 'docstyle' and prop.get('enum') and value not in prop['enum']:
                allowed = ', '.join(prop['enum'])
                raise ValueError(
                    f"Invalid value for {key}: {value}. Allowed values: {allowed}"
                )

        return True
