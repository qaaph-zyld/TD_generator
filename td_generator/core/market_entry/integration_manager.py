"""
Integration Testing and Validation System.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging
import json
import os
import asyncio
import aiohttp
from pathlib import Path
import yaml
import psutil
import docker

@dataclass
class TestCase:
    """Integration test case."""
    id: str
    name: str
    type: str
    components: List[str]
    prerequisites: List[str]
    steps: List[Dict[str, str]]
    expected: Dict[str, Any]
    actual: Optional[Dict[str, Any]] = None
    status: str = "pending"
    duration: float = 0.0
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

@dataclass
class TestSuite:
    """Integration test suite."""
    id: str
    name: str
    description: str
    test_cases: List[str]
    dependencies: List[str]
    environment: Dict[str, str]
    metrics: Dict[str, float]
    status: str
    created_at: datetime
    updated_at: datetime

@dataclass
class TestResult:
    """Test execution result."""
    test_id: str
    status: str
    duration: float
    output: Dict[str, Any]
    errors: List[str]
    metrics: Dict[str, float]
    timestamp: datetime

class IntegrationManager:
    """Manages integration testing and validation."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_cases: Dict[str, TestCase] = {}
        self.test_suites: Dict[str, TestSuite] = {}
        self.results: Dict[str, List[TestResult]] = {}
        self.storage_path = "data/integration"
        self._initialize_storage()
        self._load_test_cases()
        self.docker_client = docker.from_env()
    
    def _initialize_storage(self):
        """Initialize storage structure."""
        directories = [
            "test_cases",
            "test_suites",
            "results",
            "reports",
            "metrics"
        ]
        
        for directory in directories:
            os.makedirs(
                os.path.join(self.storage_path, directory),
                exist_ok=True
            )
    
    def _load_test_cases(self):
        """Load test cases from storage."""
        test_cases_path = os.path.join(self.storage_path, "test_cases")
        
        # Create default test cases if none exist
        if not os.listdir(test_cases_path):
            self._create_default_test_cases()
        
        # Load existing test cases
        for case_file in os.listdir(test_cases_path):
            if case_file.endswith('.json'):
                with open(os.path.join(test_cases_path, case_file), 'r') as f:
                    data = json.load(f)
                    test_case = TestCase(**data)
                    self.test_cases[test_case.id] = test_case
    
    def _create_default_test_cases(self):
        """Create default integration test cases."""
        default_cases = {
            "crm_integration": {
                "name": "CRM Integration Test",
                "type": "integration",
                "components": ["crm_setup", "crm_validation"],
                "prerequisites": ["hubspot_api_key"],
                "steps": [
                    {
                        "action": "initialize_crm",
                        "params": {"environment": "test"}
                    },
                    {
                        "action": "create_contact",
                        "params": {
                            "name": "Test User",
                            "email": "test@example.com"
                        }
                    },
                    {
                        "action": "create_deal",
                        "params": {
                            "title": "Test Deal",
                            "amount": 1000
                        }
                    },
                    {
                        "action": "validate_pipeline",
                        "params": {}
                    }
                ],
                "expected": {
                    "contact_created": True,
                    "deal_created": True,
                    "pipeline_valid": True
                }
            },
            "demo_environment": {
                "name": "Demo Environment Test",
                "type": "integration",
                "components": ["demo_setup"],
                "prerequisites": ["docker"],
                "steps": [
                    {
                        "action": "create_instance",
                        "params": {"name": "test-demo"}
                    },
                    {
                        "action": "validate_instance",
                        "params": {}
                    },
                    {
                        "action": "test_features",
                        "params": {
                            "features": [
                                "documentation_generation",
                                "multi_format_support"
                            ]
                        }
                    }
                ],
                "expected": {
                    "instance_created": True,
                    "features_working": True
                }
            },
            "collateral_system": {
                "name": "Sales Collateral Test",
                "type": "integration",
                "components": ["collateral_manager"],
                "prerequisites": [],
                "steps": [
                    {
                        "action": "create_template",
                        "params": {"type": "case_study"}
                    },
                    {
                        "action": "generate_content",
                        "params": {
                            "template": "case_study",
                            "variables": {
                                "title": "Test Case Study"
                            }
                        }
                    },
                    {
                        "action": "export_content",
                        "params": {"format": "pdf"}
                    }
                ],
                "expected": {
                    "template_created": True,
                    "content_generated": True,
                    "export_successful": True
                }
            },
            "marketing_system": {
                "name": "Marketing System Test",
                "type": "integration",
                "components": ["marketing_manager"],
                "prerequisites": [],
                "steps": [
                    {
                        "action": "create_content",
                        "params": {
                            "type": "blog",
                            "title": "Test Post"
                        }
                    },
                    {
                        "action": "create_campaign",
                        "params": {
                            "name": "Test Campaign",
                            "channels": ["blog", "social"]
                        }
                    },
                    {
                        "action": "track_metrics",
                        "params": {}
                    }
                ],
                "expected": {
                    "content_created": True,
                    "campaign_created": True,
                    "metrics_tracked": True
                }
            }
        }
        
        for case_id, case_data in default_cases.items():
            test_case = TestCase(
                id=case_id,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                **case_data
            )
            
            # Save test case
            case_path = os.path.join(
                self.storage_path,
                "test_cases",
                f"{case_id}.json"
            )
            
            with open(case_path, 'w') as f:
                json.dump(vars(test_case), f, default=str)
            
            self.test_cases[case_id] = test_case
    
    async def run_test_case(self, case_id: str) -> TestResult:
        """Run a specific test case."""
        if case_id not in self.test_cases:
            raise ValueError(f"Test case not found: {case_id}")
        
        test_case = self.test_cases[case_id]
        start_time = datetime.now()
        output = {}
        errors = []
        
        try:
            # Check prerequisites
            await self._check_prerequisites(test_case)
            
            # Execute test steps
            for step in test_case.steps:
                try:
                    step_result = await self._execute_step(step)
                    output[step["action"]] = step_result
                except Exception as e:
                    errors.append(f"Step {step['action']} failed: {str(e)}")
            
            # Validate results
            test_case.actual = output
            test_case.status = "passed" if not errors else "failed"
            
        except Exception as e:
            errors.append(f"Test execution failed: {str(e)}")
            test_case.status = "error"
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        test_case.duration = duration
        test_case.updated_at = datetime.now()
        
        # Create test result
        result = TestResult(
            test_id=case_id,
            status=test_case.status,
            duration=duration,
            output=output,
            errors=errors,
            metrics=self._calculate_metrics(output),
            timestamp=datetime.now()
        )
        
        # Save result
        self._save_result(result)
        
        # Update test case
        self._save_test_case(test_case)
        
        return result
    
    async def _check_prerequisites(self, test_case: TestCase):
        """Check test prerequisites."""
        for prereq in test_case.prerequisites:
            if prereq == "hubspot_api_key":
                if not os.getenv("HUBSPOT_API_KEY"):
                    raise ValueError("HubSpot API key not found")
            
            elif prereq == "docker":
                try:
                    self.docker_client.ping()
                except Exception:
                    raise ValueError("Docker not available")
    
    async def _execute_step(self, step: Dict[str, str]) -> Any:
        """Execute a test step."""
        action = step["action"]
        params = step["params"]
        
        if action == "initialize_crm":
            return await self._test_crm_initialization(params)
        
        elif action == "create_instance":
            return await self._test_demo_instance(params)
        
        elif action == "create_content":
            return await self._test_content_creation(params)
        
        elif action == "track_metrics":
            return await self._test_metric_tracking(params)
        
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _test_crm_initialization(self, params: Dict) -> Dict:
        """Test CRM initialization."""
        # Implement CRM testing logic
        return {"initialized": True, "environment": params["environment"]}
    
    async def _test_demo_instance(self, params: Dict) -> Dict:
        """Test demo instance creation."""
        # Implement demo testing logic
        return {"created": True, "name": params["name"]}
    
    async def _test_content_creation(self, params: Dict) -> Dict:
        """Test content creation."""
        # Implement content testing logic
        return {"created": True, "type": params["type"]}
    
    async def _test_metric_tracking(self, params: Dict) -> Dict:
        """Test metric tracking."""
        # Implement metric testing logic
        return {"tracked": True, "timestamp": datetime.now().isoformat()}
    
    def _calculate_metrics(self, output: Dict[str, Any]) -> Dict[str, float]:
        """Calculate test metrics."""
        return {
            "success_rate": len([v for v in output.values() if v.get("created", False)]) / len(output),
            "error_rate": len([v for v in output.values() if not v.get("created", False)]) / len(output)
        }
    
    def _save_result(self, result: TestResult):
        """Save test result."""
        if result.test_id not in self.results:
            self.results[result.test_id] = []
        
        self.results[result.test_id].append(result)
        
        # Save to storage
        result_path = os.path.join(
            self.storage_path,
            "results",
            f"{result.test_id}-{result.timestamp.strftime('%Y%m%d-%H%M%S')}.json"
        )
        
        with open(result_path, 'w') as f:
            json.dump(vars(result), f, default=str)
    
    def _save_test_case(self, test_case: TestCase):
        """Save test case."""
        case_path = os.path.join(
            self.storage_path,
            "test_cases",
            f"{test_case.id}.json"
        )
        
        with open(case_path, 'w') as f:
            json.dump(vars(test_case), f, default=str)
    
    def create_test_suite(
        self,
        name: str,
        description: str,
        test_cases: List[str],
        environment: Dict[str, str]
    ) -> TestSuite:
        """Create new test suite."""
        # Validate test cases
        invalid_cases = set(test_cases) - set(self.test_cases.keys())
        if invalid_cases:
            raise ValueError(f"Invalid test cases: {invalid_cases}")
        
        # Create suite
        suite = TestSuite(
            id=f"suite-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=name,
            description=description,
            test_cases=test_cases,
            dependencies=list(set(
                dep
                for case_id in test_cases
                for dep in self.test_cases[case_id].prerequisites
            )),
            environment=environment,
            metrics={},
            status="pending",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Save suite
        self._save_suite(suite)
        self.test_suites[suite.id] = suite
        
        self.logger.info(f"Created test suite: {suite.id}")
        return suite
    
    def _save_suite(self, suite: TestSuite):
        """Save test suite."""
        suite_path = os.path.join(
            self.storage_path,
            "test_suites",
            f"{suite.id}.json"
        )
        
        with open(suite_path, 'w') as f:
            json.dump(vars(suite), f, default=str)
    
    async def run_test_suite(self, suite_id: str) -> Dict[str, TestResult]:
        """Run all tests in a suite."""
        if suite_id not in self.test_suites:
            raise ValueError(f"Test suite not found: {suite_id}")
        
        suite = self.test_suites[suite_id]
        results = {}
        
        try:
            # Run all test cases
            for case_id in suite.test_cases:
                results[case_id] = await self.run_test_case(case_id)
            
            # Update suite metrics
            suite.metrics = self._calculate_suite_metrics(results)
            suite.status = "passed" if all(
                r.status == "passed" for r in results.values()
            ) else "failed"
            
        except Exception as e:
            self.logger.error(f"Suite execution failed: {str(e)}")
            suite.status = "error"
        
        suite.updated_at = datetime.now()
        self._save_suite(suite)
        
        return results
    
    def _calculate_suite_metrics(
        self,
        results: Dict[str, TestResult]
    ) -> Dict[str, float]:
        """Calculate test suite metrics."""
        return {
            "total_duration": sum(r.duration for r in results.values()),
            "success_rate": len([
                r for r in results.values()
                if r.status == "passed"
            ]) / len(results),
            "error_rate": len([
                r for r in results.values()
                if r.status == "error"
            ]) / len(results)
        }
    
    def get_test_results(
        self,
        test_id: str,
        limit: int = 10
    ) -> List[TestResult]:
        """Get recent test results."""
        if test_id not in self.results:
            return []
        
        return sorted(
            self.results[test_id],
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]
    
    def get_status(self) -> Dict:
        """Get integration testing status."""
        return {
            "test_cases": {
                "total": len(self.test_cases),
                "by_status": {
                    status: len([
                        t for t in self.test_cases.values()
                        if t.status == status
                    ])
                    for status in {"pending", "passed", "failed", "error"}
                }
            },
            "test_suites": {
                "total": len(self.test_suites),
                "active": len([
                    s for s in self.test_suites.values()
                    if s.status == "pending"
                ])
            },
            "results": {
                "total": sum(len(results) for results in self.results.values()),
                "by_status": {
                    status: len([
                        r
                        for results in self.results.values()
                        for r in results
                        if r.status == status
                    ])
                    for status in {"passed", "failed", "error"}
                }
            },
            "system": {
                "cpu_usage": psutil.cpu_percent(),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            }
        }
