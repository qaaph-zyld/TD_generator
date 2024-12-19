"""
Sales Collateral Management System.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime
import logging
import json
import os
import shutil
from pathlib import Path
import markdown
import jinja2

@dataclass
class CollateralItem:
    """Sales collateral item."""
    id: str
    title: str
    type: str
    format: str
    content: str
    variables: Dict[str, str]
    created_at: datetime
    updated_at: datetime
    version: str

@dataclass
class CollateralTemplate:
    """Collateral template definition."""
    id: str
    name: str
    type: str
    format: str
    template: str
    variables: List[str]
    created_at: datetime

class CollateralManager:
    """Manages sales collateral creation and distribution."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.items: Dict[str, CollateralItem] = {}
        self.templates: Dict[str, CollateralTemplate] = {}
        self.storage_path = "data/collateral"
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("templates/collateral")
        )
        self._initialize_storage()
        self._load_templates()
    
    def _initialize_storage(self):
        """Initialize storage structure."""
        directories = [
            "presentations",
            "case_studies",
            "white_papers",
            "data_sheets",
            "roi_calculator",
            "templates"
        ]
        
        for directory in directories:
            os.makedirs(
                os.path.join(self.storage_path, directory),
                exist_ok=True
            )
    
    def _load_templates(self):
        """Load collateral templates."""
        template_dir = os.path.join(self.storage_path, "templates")
        
        # Create default templates if none exist
        if not os.listdir(template_dir):
            self._create_default_templates()
        
        # Load existing templates
        for template_file in os.listdir(template_dir):
            if template_file.endswith('.json'):
                with open(os.path.join(template_dir, template_file), 'r') as f:
                    data = json.load(f)
                    template = CollateralTemplate(**data)
                    self.templates[template.id] = template
    
    def _create_default_templates(self):
        """Create default collateral templates."""
        default_templates = {
            "case_study": {
                "name": "Case Study Template",
                "type": "case_study",
                "format": "markdown",
                "template": """# {{company_name}} Case Study

## Overview
{{company_description}}

## Challenge
{{challenge_description}}

## Solution
{{solution_description}}

## Results
{{results_description}}

## ROI Metrics
- Implementation Time: {{implementation_time}}
- Cost Savings: {{cost_savings}}
- Efficiency Gain: {{efficiency_gain}}

## Testimonial
> {{testimonial_quote}}
> 
> — {{testimonial_author}}, {{testimonial_title}}
""",
                "variables": [
                    "company_name",
                    "company_description",
                    "challenge_description",
                    "solution_description",
                    "results_description",
                    "implementation_time",
                    "cost_savings",
                    "efficiency_gain",
                    "testimonial_quote",
                    "testimonial_author",
                    "testimonial_title"
                ]
            },
            "data_sheet": {
                "name": "Product Data Sheet",
                "type": "data_sheet",
                "format": "markdown",
                "template": """# {{product_name}}

## Product Overview
{{product_description}}

## Key Features
{{features}}

## Technical Specifications
{{specifications}}

## System Requirements
{{requirements}}

## Pricing
{{pricing_details}}

## Support
{{support_details}}
""",
                "variables": [
                    "product_name",
                    "product_description",
                    "features",
                    "specifications",
                    "requirements",
                    "pricing_details",
                    "support_details"
                ]
            },
            "roi_calculator": {
                "name": "ROI Calculator Template",
                "type": "roi_calculator",
                "format": "markdown",
                "template": """# ROI Analysis: {{company_name}}

## Current Process Costs
- Documentation Time: {{current_doc_time}} hours/month
- Review Cycles: {{current_review_cycles}} cycles
- Error Rate: {{current_error_rate}}%
- Monthly Cost: ${{current_monthly_cost}}

## Projected Savings with TD Generator
- Documentation Time: {{new_doc_time}} hours/month
- Review Cycles: {{new_review_cycles}} cycles
- Error Rate: {{new_error_rate}}%
- Monthly Cost: ${{new_monthly_cost}}

## ROI Metrics
- Monthly Savings: ${{monthly_savings}}
- Annual Savings: ${{annual_savings}}
- ROI: {{roi_percentage}}%
- Payback Period: {{payback_period}} months

## Additional Benefits
{{additional_benefits}}
""",
                "variables": [
                    "company_name",
                    "current_doc_time",
                    "current_review_cycles",
                    "current_error_rate",
                    "current_monthly_cost",
                    "new_doc_time",
                    "new_review_cycles",
                    "new_error_rate",
                    "new_monthly_cost",
                    "monthly_savings",
                    "annual_savings",
                    "roi_percentage",
                    "payback_period",
                    "additional_benefits"
                ]
            }
        }
        
        for template_id, template_data in default_templates.items():
            template = CollateralTemplate(
                id=template_id,
                created_at=datetime.now(),
                **template_data
            )
            
            # Save template
            template_path = os.path.join(
                self.storage_path,
                "templates",
                f"{template_id}.json"
            )
            
            with open(template_path, 'w') as f:
                json.dump(vars(template), f, default=str)
            
            self.templates[template_id] = template
    
    def create_collateral(
        self,
        template_id: str,
        variables: Dict[str, str]
    ) -> CollateralItem:
        """Create new collateral item from template."""
        if template_id not in self.templates:
            raise ValueError(f"Template not found: {template_id}")
        
        template = self.templates[template_id]
        
        # Validate variables
        missing_vars = set(template.variables) - set(variables.keys())
        if missing_vars:
            raise ValueError(f"Missing variables: {missing_vars}")
        
        # Generate content
        template_obj = self.template_env.from_string(template.template)
        content = template_obj.render(**variables)
        
        # Create collateral item
        item = CollateralItem(
            id=f"{template_id}-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            title=variables.get('title', 'Untitled'),
            type=template.type,
            format=template.format,
            content=content,
            variables=variables,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            version="1.0.0"
        )
        
        # Save item
        self._save_collateral(item)
        self.items[item.id] = item
        
        self.logger.info(f"Created collateral: {item.id}")
        return item
    
    def _save_collateral(self, item: CollateralItem):
        """Save collateral item to storage."""
        type_dir = os.path.join(self.storage_path, item.type)
        
        # Save content
        content_path = os.path.join(type_dir, f"{item.id}.{item.format}")
        with open(content_path, 'w') as f:
            f.write(item.content)
        
        # Save metadata
        meta_path = os.path.join(type_dir, f"{item.id}.json")
        with open(meta_path, 'w') as f:
            json.dump(vars(item), f, default=str)
    
    def update_collateral(
        self,
        item_id: str,
        variables: Dict[str, str]
    ) -> CollateralItem:
        """Update existing collateral item."""
        if item_id not in self.items:
            raise ValueError(f"Item not found: {item_id}")
        
        item = self.items[item_id]
        template = self.templates[item.type]
        
        # Update variables
        item.variables.update(variables)
        
        # Regenerate content
        template_obj = self.template_env.from_string(template.template)
        item.content = template_obj.render(**item.variables)
        
        # Update metadata
        item.updated_at = datetime.now()
        version_parts = item.version.split('.')
        item.version = f"{version_parts[0]}.{version_parts[1]}.{int(version_parts[2])+1}"
        
        # Save updates
        self._save_collateral(item)
        
        self.logger.info(f"Updated collateral: {item_id}")
        return item
    
    def get_collateral(self, item_id: str) -> Optional[CollateralItem]:
        """Get collateral item."""
        return self.items.get(item_id)
    
    def list_collateral(self, type: Optional[str] = None) -> List[CollateralItem]:
        """List collateral items."""
        items = self.items.values()
        if type:
            items = [i for i in items if i.type == type]
        return sorted(items, key=lambda x: x.updated_at, reverse=True)
    
    def export_collateral(
        self,
        item_id: str,
        format: str = "pdf"
    ) -> str:
        """Export collateral item to different format."""
        if item_id not in self.items:
            raise ValueError(f"Item not found: {item_id}")
        
        item = self.items[item_id]
        
        if format == "html":
            if item.format == "markdown":
                return markdown.markdown(item.content)
            return item.content
        
        elif format == "pdf":
            # PDF conversion would go here
            raise NotImplementedError("PDF export not implemented")
        
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def get_template(self, template_id: str) -> Optional[CollateralTemplate]:
        """Get template by ID."""
        return self.templates.get(template_id)
    
    def list_templates(self) -> List[CollateralTemplate]:
        """List available templates."""
        return sorted(
            self.templates.values(),
            key=lambda x: x.created_at
        )
    
    def get_status(self) -> Dict:
        """Get collateral system status."""
        return {
            "items": {
                "total": len(self.items),
                "by_type": {
                    type: len([i for i in self.items.values() if i.type == type])
                    for type in set(i.type for i in self.items.values())
                }
            },
            "templates": {
                "total": len(self.templates),
                "types": list(self.templates.keys())
            },
            "storage": {
                "path": self.storage_path,
                "size": sum(
                    os.path.getsize(os.path.join(root, file))
                    for root, _, files in os.walk(self.storage_path)
                    for file in files
                )
            }
        }
