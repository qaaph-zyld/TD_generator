"""
Template management system for documentation generation.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging
import jinja2

@dataclass
class TemplateConfig:
    name: str
    format: str
    variables: Dict
    sections: List[str]
    style_overrides: Optional[Dict] = None

class Template:
    def __init__(self, config: TemplateConfig):
        self.config = config
        self.template = None
        self.logger = logging.getLogger(__name__)
    
    def load(self, content: str):
        """Load template content."""
        try:
            self.template = jinja2.Template(content)
        except Exception as e:
            self.logger.error(f"Failed to load template: {str(e)}")
            raise
    
    def render(self, context: Dict) -> str:
        """Render template with context."""
        try:
            return self.template.render(**context)
        except Exception as e:
            self.logger.error(f"Failed to render template: {str(e)}")
            raise
    
    def validate(self) -> bool:
        """Validate template configuration."""
        required_sections = {'header', 'content', 'footer'}
        return all(section in self.config.sections for section in required_sections)

class TemplateRegistry:
    """Registry for managing documentation templates."""
    
    def __init__(self):
        self.templates: Dict[str, Template] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_template(self, template_id: str, template: Template):
        """Register a new template."""
        if template_id in self.templates:
            self.logger.warning(f"Overwriting existing template: {template_id}")
        self.templates[template_id] = template
        self.logger.info(f"Registered template: {template_id}")
    
    def get_template(self, template_id: str) -> Template:
        """Get template by ID."""
        if template_id not in self.templates:
            raise KeyError(f"Template not found: {template_id}")
        return self.templates[template_id]
    
    def list_templates(self) -> List[str]:
        """List all registered templates."""
        return list(self.templates.keys())

class TemplateManager:
    """Manager for template operations."""
    
    def __init__(self):
        self.registry = TemplateRegistry()
        self.logger = logging.getLogger(__name__)
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default templates."""
        default_templates = {
            'code': self._create_code_template(),
            'api': self._create_api_template(),
            'markdown': self._create_markdown_template()
        }
        
        for template_id, template in default_templates.items():
            self.registry.register_template(template_id, template)
    
    def _create_code_template(self) -> Template:
        """Create default code documentation template."""
        config = TemplateConfig(
            name='Default Code Template',
            format='code',
            variables={
                'title': '',
                'description': '',
                'classes': [],
                'functions': []
            },
            sections=['header', 'overview', 'classes', 'functions', 'footer']
        )
        
        template = Template(config)
        template.load("""
# {{ title }}

{{ description }}

{% if classes %}
## Classes

{% for class in classes %}
### {{ class.name }}
{{ class.description }}

#### Methods
{% for method in class.methods %}
- `{{ method.name }}`: {{ method.description }}
{% endfor %}
{% endfor %}
{% endif %}

{% if functions %}
## Functions

{% for function in functions %}
### `{{ function.name }}`
{{ function.description }}

#### Parameters
{% for param in function.parameters %}
- `{{ param.name }}`: {{ param.description }}
{% endfor %}

#### Returns
{{ function.returns }}
{% endfor %}
{% endif %}
        """)
        
        return template
    
    def _create_api_template(self) -> Template:
        """Create default API documentation template."""
        config = TemplateConfig(
            name='Default API Template',
            format='api',
            variables={
                'title': '',
                'description': '',
                'version': '',
                'endpoints': []
            },
            sections=['header', 'overview', 'authentication', 'endpoints', 'footer']
        )
        
        template = Template(config)
        template.load("""
# {{ title }} API Documentation

Version: {{ version }}

{{ description }}

## Authentication
{{ authentication }}

## Endpoints

{% for endpoint in endpoints %}
### {{ endpoint.method }} {{ endpoint.path }}
{{ endpoint.description }}

#### Request
```json
{{ endpoint.request }}
```

#### Response
```json
{{ endpoint.response }}
```

{% if endpoint.examples %}
#### Examples
{% for example in endpoint.examples %}
{{ example }}
{% endfor %}
{% endif %}
{% endfor %}
        """)
        
        return template
    
    def _create_markdown_template(self) -> Template:
        """Create default markdown documentation template."""
        config = TemplateConfig(
            name='Default Markdown Template',
            format='markdown',
            variables={
                'title': '',
                'description': '',
                'sections': []
            },
            sections=['header', 'content', 'footer']
        )
        
        template = Template(config)
        template.load("""
# {{ title }}

{{ description }}

{% for section in sections %}
## {{ section.title }}

{{ section.content }}
{% endfor %}
        """)
        
        return template
    
    def create_template(self, config: TemplateConfig, content: str) -> str:
        """Create a new template."""
        try:
            template = Template(config)
            template.load(content)
            
            if not template.validate():
                raise ValueError("Invalid template configuration")
            
            template_id = f"{config.format}_{config.name}"
            self.registry.register_template(template_id, template)
            
            return template_id
            
        except Exception as e:
            self.logger.error(f"Failed to create template: {str(e)}")
            raise
    
    def render_template(self, template_id: str, context: Dict) -> str:
        """Render a template with context."""
        try:
            template = self.registry.get_template(template_id)
            return template.render(context)
        except Exception as e:
            self.logger.error(f"Failed to render template: {str(e)}")
            raise
    
    def get_template_config(self, template_id: str) -> TemplateConfig:
        """Get template configuration."""
        template = self.registry.get_template(template_id)
        return template.config
