"""
Advanced prompting patterns for TD Generator.
"""
from typing import Dict, Optional

class PromptTemplate:
    def __init__(self, template: str):
        self.template = template
    
    def format(self, **kwargs) -> str:
        """Formats the prompt template with provided values."""
        return self.template.format(**kwargs)

# Documentation Generation Prompts
DOCUMENTATION_PROMPT = PromptTemplate("""
<ScopeAlignmentProtocol>
    <CurrentObjective>
        Generate technical documentation while maintaining:
        1. Absolute scope integrity
        2. Architectural consistency
        3. Implementation traceability
    </CurrentObjective>

    <ValidationCriteria>
        - Direct mapping to project charter
        - Explicit alignment with architectural decisions
        - Clear traceability to requirements
    </ValidationCriteria>

    <ContentGeneration>
        Documentation Task: {task_description}
        Scope Boundaries: {scope_definition}
        Required Alignment: {alignment_criteria}
    </ContentGeneration>
</ScopeAlignmentProtocol>

Generate documentation that:
1. Maintains strict adherence to project scope
2. Implements progressive disclosure principles
3. Ensures technical accuracy and completeness
""")

# Implementation Verification Prompts
VERIFICATION_PROMPT = PromptTemplate("""
<VerificationFramework>
    <CorePrinciples>
        - Systematic validation approach
        - Multi-layer verification
        - Explicit traceability
    </CorePrinciples>

    <ValidationSteps>
        1. Requirements Alignment
        2. Architectural Consistency
        3. Performance Optimization
        4. Resource Efficiency
    </ValidationSteps>

    <ComplianceChecks>
        Implementation: {implementation_details}
        Original Scope: {scope_definition}
        Performance Metrics: {performance_criteria}
    </ComplianceChecks>
</VerificationFramework>

Verify implementation against:
1. Original project charter
2. Architectural specifications
3. Performance requirements
""")

class PromptManager:
    def __init__(self):
        self.documentation_prompt = DOCUMENTATION_PROMPT
        self.verification_prompt = VERIFICATION_PROMPT
    
    def get_documentation_prompt(self,
                               task_description: str,
                               scope_definition: str,
                               alignment_criteria: str) -> str:
        """Gets formatted documentation prompt."""
        return self.documentation_prompt.format(
            task_description=task_description,
            scope_definition=scope_definition,
            alignment_criteria=alignment_criteria
        )
    
    def get_verification_prompt(self,
                              implementation_details: Dict,
                              scope_definition: str,
                              performance_criteria: Dict) -> str:
        """Gets formatted verification prompt."""
        return self.verification_prompt.format(
            implementation_details=implementation_details,
            scope_definition=scope_definition,
            performance_criteria=performance_criteria
        )
