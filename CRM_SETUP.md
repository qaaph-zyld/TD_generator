# CRM Setup Guide

## Overview
This guide details the setup and validation of our HubSpot CRM integration for TD Generator.

## Prerequisites
1. HubSpot account
2. API key with appropriate permissions
3. Portal ID from HubSpot

## Configuration

### 1. Environment Variables
Set the following environment variables:
```bash
HUBSPOT_API_KEY=your_api_key_here
HUBSPOT_PORTAL_ID=your_portal_id_here
```

### 2. Pipeline Configuration
The system will automatically create a sales pipeline with the following stages:
1. Lead (20% probability)
2. Contact Made (40% probability)
3. Demo Scheduled (60% probability)
4. Trial (80% probability)
5. Negotiation (90% probability)
6. Closed Won (100% probability)
7. Closed Lost (0% probability)

## Implementation Steps

### 1. Initialize CRM
```python
from td_generator.core.market_entry.crm_setup import CRMSetupManager

# Create CRM manager
crm = CRMSetupManager()

# Initialize CRM setup
crm.initialize()
```

### 2. Validate Setup
```python
from td_generator.core.market_entry.crm_validation import CRMValidator
import asyncio

# Create validator
validator = CRMValidator(crm)

# Run validation suite
results = asyncio.run(validator.run_validation_suite())

# Generate report
report = validator.generate_validation_report()
print(report)
```

### 3. Create Test Data
```python
# Create test contact and deal
test_data = crm.create_test_data()
print(f"Created test contact: {test_data['contact_id']}")
print(f"Created test deal: {test_data['deal_id']}")
```

## Validation Checks

### 1. Configuration Validation
- API key presence
- Pipeline configuration
- Portal ID validation

### 2. Pipeline Validation
- Stage configuration
- Stage progression
- Probability settings

### 3. Contact Management
- Contact creation
- Contact updates
- Field mapping

### 4. Deal Management
- Deal creation
- Stage updates
- Amount tracking

### 5. Metrics Collection
- Pipeline metrics
- Stage metrics
- Deal values

## Monitoring

### 1. Status Check
```python
# Get CRM status
status = crm.get_status()
print(f"CRM Status: {status['status']}")
print(f"Pipeline ID: {status['pipeline_id']}")
```

### 2. Pipeline Metrics
```python
# Get pipeline metrics
metrics = crm.hubspot.get_pipeline_metrics()
for stage, data in metrics.items():
    print(f"{stage}: {data['deals']} deals, ${data['value']}")
```

## Troubleshooting

### Common Issues
1. **API Key Invalid**
   - Verify key in environment variables
   - Check HubSpot permissions

2. **Pipeline Creation Failed**
   - Check portal permissions
   - Verify stage configuration

3. **Contact Creation Failed**
   - Validate required fields
   - Check email format

### Error Resolution
1. Check logs for detailed error messages
2. Validate configuration settings
3. Run validation suite for diagnostics
4. Contact HubSpot support if needed

## Next Steps

1. **Data Migration**
   - Import existing contacts
   - Set up custom fields
   - Configure workflows

2. **Integration Testing**
   - Test full sales cycle
   - Validate metrics
   - Check automation

3. **Team Training**
   - Pipeline management
   - Contact handling
   - Reporting system
