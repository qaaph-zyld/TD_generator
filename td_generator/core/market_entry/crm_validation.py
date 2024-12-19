"""
CRM Validation and Testing Module.
"""
from typing import Dict, List
import logging
from datetime import datetime, timedelta
import asyncio
from .crm_setup import CRMSetupManager, Contact

class CRMValidator:
    """Validates CRM setup and functionality."""
    
    def __init__(self, crm_manager: CRMSetupManager):
        self.crm = crm_manager
        self.logger = logging.getLogger(__name__)
        self.validation_results = {}
    
    async def run_validation_suite(self) -> Dict:
        """Run comprehensive validation suite."""
        self.logger.info("Starting CRM validation suite")
        
        # Run validations concurrently
        validation_tasks = [
            self._validate_configuration(),
            self._validate_pipeline(),
            self._validate_contact_creation(),
            self._validate_deal_flow(),
            self._validate_metrics()
        ]
        
        results = await asyncio.gather(*validation_tasks)
        
        # Aggregate results
        self.validation_results = {
            "configuration": results[0],
            "pipeline": results[1],
            "contact_creation": results[2],
            "deal_flow": results[3],
            "metrics": results[4],
            "timestamp": datetime.now().isoformat(),
            "overall_status": all(r.get("status") == "passed" for r in results)
        }
        
        return self.validation_results
    
    async def _validate_configuration(self) -> Dict:
        """Validate CRM configuration."""
        try:
            if not self.crm.config.api_key:
                return {
                    "status": "failed",
                    "error": "API key not configured"
                }
            
            if not self.crm.config.pipeline_id:
                return {
                    "status": "failed",
                    "error": "Pipeline not configured"
                }
            
            return {
                "status": "passed",
                "details": {
                    "api_key": "configured",
                    "pipeline": "configured"
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _validate_pipeline(self) -> Dict:
        """Validate sales pipeline setup."""
        try:
            metrics = self.crm.hubspot.get_pipeline_metrics()
            
            if not metrics:
                return {
                    "status": "failed",
                    "error": "Pipeline metrics not available"
                }
            
            expected_stages = {
                stage["label"]
                for stage in self.crm.config.stages
            }
            
            actual_stages = set(metrics.keys())
            
            if expected_stages != actual_stages:
                return {
                    "status": "failed",
                    "error": f"Pipeline stages mismatch. Expected: {expected_stages}, Got: {actual_stages}"
                }
            
            return {
                "status": "passed",
                "details": {
                    "stages": list(actual_stages)
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _validate_contact_creation(self) -> Dict:
        """Validate contact creation functionality."""
        try:
            test_contact = Contact(
                email=f"test_{datetime.now().timestamp()}@example.com",
                first_name="Validation",
                last_name="Test",
                company="Test Corp",
                title="CTO",
                status="LEAD",
                created_at=datetime.now()
            )
            
            contact_id = self.crm.hubspot.create_contact(test_contact)
            
            if not contact_id:
                return {
                    "status": "failed",
                    "error": "Contact creation failed"
                }
            
            return {
                "status": "passed",
                "details": {
                    "contact_id": contact_id
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _validate_deal_flow(self) -> Dict:
        """Validate deal creation and stage updates."""
        try:
            # Create test contact
            test_contact = Contact(
                email=f"deal_test_{datetime.now().timestamp()}@example.com",
                first_name="Deal",
                last_name="Test",
                company="Test Corp",
                title="CTO",
                status="LEAD",
                created_at=datetime.now()
            )
            
            contact_id = self.crm.hubspot.create_contact(test_contact)
            
            # Create deal
            deal_id = self.crm.hubspot.create_deal(
                contact_id=contact_id,
                amount=1000.0,
                stage="Lead"
            )
            
            if not deal_id:
                return {
                    "status": "failed",
                    "error": "Deal creation failed"
                }
            
            # Update deal stage
            self.crm.hubspot.update_deal_stage(deal_id, "Contact Made")
            
            return {
                "status": "passed",
                "details": {
                    "contact_id": contact_id,
                    "deal_id": deal_id
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _validate_metrics(self) -> Dict:
        """Validate metrics collection."""
        try:
            metrics = self.crm.hubspot.get_pipeline_metrics()
            
            if not isinstance(metrics, dict):
                return {
                    "status": "failed",
                    "error": "Invalid metrics format"
                }
            
            # Validate metrics structure
            for stage, data in metrics.items():
                if not isinstance(data, dict):
                    return {
                        "status": "failed",
                        "error": f"Invalid metrics data for stage: {stage}"
                    }
                
                if "deals" not in data or "value" not in data:
                    return {
                        "status": "failed",
                        "error": f"Missing metrics fields for stage: {stage}"
                    }
            
            return {
                "status": "passed",
                "details": {
                    "metrics": metrics
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def generate_validation_report(self) -> str:
        """Generate human-readable validation report."""
        if not self.validation_results:
            return "No validation results available"
        
        report = []
        report.append("# CRM Validation Report")
        report.append(f"Generated: {self.validation_results['timestamp']}")
        report.append("")
        
        # Overall status
        status = "✅ PASSED" if self.validation_results["overall_status"] else "❌ FAILED"
        report.append(f"Overall Status: {status}")
        report.append("")
        
        # Individual validations
        for name, result in self.validation_results.items():
            if name in ["timestamp", "overall_status"]:
                continue
                
            status = "✅" if result["status"] == "passed" else "❌"
            report.append(f"## {name.replace('_', ' ').title()} {status}")
            
            if result["status"] == "passed":
                report.append("Status: PASSED")
                if "details" in result:
                    for key, value in result["details"].items():
                        report.append(f"- {key}: {value}")
            else:
                report.append(f"Status: FAILED - {result.get('error', 'Unknown error')}")
            
            report.append("")
        
        return "\n".join(report)
