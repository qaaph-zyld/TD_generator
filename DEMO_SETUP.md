# Demo Environment Setup Guide

## Overview
This guide details the setup and management of the TD Generator demo environment.

## Prerequisites
1. Docker installed and running
2. Python 3.9 or higher
3. Network access for port 8000

## Components

### 1. Demo Environment
- Containerized TD Generator instance
- Sample documentation projects
- Test cases and templates
- Monitoring and metrics

### 2. Demo Data
- Project templates
- Sample documentation
- Test documentation
- Configuration files

## Setup Instructions

### 1. Initialize Environment
```python
from td_generator.core.market_entry.demo_setup import DemoOrchestrator

# Create orchestrator
demo = DemoOrchestrator()

# Initialize environment
demo.initialize()
```

### 2. Create Demo Instance
```python
# Create new demo
instance = demo.create_demo("customer1")

print(f"Demo URL: {instance['url']}")
print(f"Credentials: {instance['credentials']}")
```

### 3. Monitor Status
```python
# Get environment status
status = demo.get_status()
print(f"Active instances: {status['instances']['active']}")
print(f"Available features: {status['features']}")
```

## Demo Data Structure

### 1. Project Templates
- API documentation templates
- User guide templates
- Technical specification templates

### 2. Sample Documentation
- REST API documentation
- Deployment guides
- Architecture documentation

### 3. Test Cases
- API documentation tests
- Format conversion tests
- Quality validation tests

## Management Features

### 1. Instance Management
- Create new instances
- Stop instances
- Monitor status
- Cleanup expired

### 2. Data Management
- Template management
- Sample data updates
- Configuration control

### 3. Monitoring
- Instance status
- Resource usage
- Feature availability

## Demo Flow

### 1. Initial Setup
1. Environment initialization
2. Data preparation
3. Instance creation

### 2. Customer Demo
1. Access demo instance
2. Feature demonstration
3. Documentation generation
4. Result review

### 3. Cleanup
1. Stop instance
2. Clean temporary data
3. Update metrics

## Troubleshooting

### Common Issues
1. **Port Conflicts**
   - Check port availability
   - Stop conflicting services
   - Use alternative port

2. **Resource Constraints**
   - Monitor Docker resources
   - Clean unused containers
   - Adjust resource limits

3. **Data Access**
   - Verify file permissions
   - Check path configuration
   - Update demo data

### Resolution Steps
1. Check logs for errors
2. Verify configuration
3. Restart services if needed
4. Contact support team

## Best Practices

### 1. Demo Preparation
- Verify environment status
- Update demo data
- Test features
- Prepare scenarios

### 2. During Demo
- Monitor performance
- Track feature usage
- Collect feedback
- Document issues

### 3. Post-Demo
- Clean up resources
- Update documentation
- Process feedback
- Plan improvements

## Next Steps

1. **Environment Enhancement**
   - Add more templates
   - Expand test cases
   - Improve monitoring

2. **Feature Integration**
   - New capabilities
   - Enhanced workflows
   - Better visualization

3. **Documentation Updates**
   - Usage guidelines
   - Best practices
   - Success stories
