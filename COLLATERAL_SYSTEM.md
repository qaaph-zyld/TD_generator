# Sales Collateral System Guide

## Overview
The Sales Collateral System manages the creation, maintenance, and distribution of sales materials for TD Generator.

## Components

### 1. Collateral Types
- Case Studies
- Data Sheets
- ROI Calculator
- White Papers
- Presentations

### 2. Template System
- Markdown templates
- Variable substitution
- Version control
- Format conversion

### 3. Storage System
- Organized structure
- Metadata management
- Version tracking
- Export capabilities

## Usage Guide

### 1. Create Collateral
```python
from td_generator.core.market_entry.collateral_manager import CollateralManager

# Initialize manager
manager = CollateralManager()

# Create case study
case_study = manager.create_collateral(
    template_id="case_study",
    variables={
        "company_name": "Tech Corp",
        "company_description": "Leading software company",
        "challenge_description": "Manual documentation process",
        "solution_description": "Implemented TD Generator",
        "results_description": "70% time savings",
        "implementation_time": "2 weeks",
        "cost_savings": "$50,000/year",
        "efficiency_gain": "3x faster documentation",
        "testimonial_quote": "Game-changing solution",
        "testimonial_author": "John Smith",
        "testimonial_title": "CTO"
    }
)

print(f"Created case study: {case_study.id}")
```

### 2. Update Collateral
```python
# Update existing collateral
updated = manager.update_collateral(
    item_id=case_study.id,
    variables={
        "cost_savings": "$75,000/year",
        "efficiency_gain": "4x faster documentation"
    }
)

print(f"Updated version: {updated.version}")
```

### 3. Export Collateral
```python
# Export to HTML
html_content = manager.export_collateral(
    item_id=case_study.id,
    format="html"
)

print("Exported to HTML")
```

## Template System

### 1. Case Study Template
- Company overview
- Challenge description
- Solution details
- Results and metrics
- Customer testimonial

### 2. Data Sheet Template
- Product overview
- Key features
- Technical specs
- System requirements
- Pricing details

### 3. ROI Calculator Template
- Current costs
- Projected savings
- ROI metrics
- Additional benefits

## Best Practices

### 1. Content Creation
- Use clear, concise language
- Include specific metrics
- Add customer quotes
- Maintain consistency

### 2. Template Usage
- Fill all variables
- Review content
- Version appropriately
- Test formatting

### 3. Management
- Regular updates
- Version control
- Backup system
- Quality checks

## Storage Structure

### 1. Directory Layout
```
data/collateral/
├── presentations/
├── case_studies/
├── white_papers/
├── data_sheets/
├── roi_calculator/
└── templates/
```

### 2. File Organization
- Content files (.md)
- Metadata files (.json)
- Template definitions
- Export formats

### 3. Version Control
- Version numbering
- Change tracking
- History maintenance
- Rollback capability

## Next Steps

### 1. Content Development
- Create case studies
- Develop data sheets
- Build presentations
- Configure calculator

### 2. System Enhancement
- Add more templates
- Improve exports
- Enhanced tracking
- Analytics integration

### 3. Integration
- CRM connection
- Demo environment
- Website content
- Email templates
