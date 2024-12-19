"""
Multi-format content processing system.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
import ast
import logging
import re

@dataclass
class ProcessingResult:
    content_type: str
    structured_content: Dict
    metadata: Dict
    analysis: Dict

class FormatProcessor(ABC):
    """Base class for format-specific processors."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    @abstractmethod
    async def process(self, content: str) -> ProcessingResult:
        """Process content in specific format."""
        pass
    
    @abstractmethod
    def validate_format(self, content: str) -> bool:
        """Validate if content matches expected format."""
        pass

class CodeProcessor(FormatProcessor):
    """Processes source code content."""
    
    async def process(self, content: str) -> ProcessingResult:
        """Process source code content."""
        try:
            # Parse code into AST
            tree = ast.parse(content)
            
            # Extract structural information
            structure = self._analyze_code_structure(tree)
            
            # Extract documentation elements
            docs = self._extract_documentation(tree)
            
            # Analyze complexity
            complexity = self._analyze_complexity(tree)
            
            return ProcessingResult(
                content_type='code',
                structured_content={
                    'structure': structure,
                    'documentation': docs
                },
                metadata={
                    'language': 'python',
                    'complexity_score': complexity['score']
                },
                analysis=complexity
            )
            
        except Exception as e:
            self.logger.error(f"Code processing failed: {str(e)}")
            raise
    
    def validate_format(self, content: str) -> bool:
        """Validate if content is valid Python code."""
        try:
            ast.parse(content)
            return True
        except SyntaxError:
            return False
    
    def _analyze_code_structure(self, tree: ast.AST) -> Dict:
        """Analyze code structure from AST."""
        structure = {
            'classes': [],
            'functions': [],
            'imports': []
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                structure['classes'].append({
                    'name': node.name,
                    'methods': [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                })
            elif isinstance(node, ast.FunctionDef):
                structure['functions'].append({
                    'name': node.name,
                    'args': [a.arg for a in node.args.args]
                })
            elif isinstance(node, ast.Import):
                structure['imports'].extend(n.name for n in node.names)
        
        return structure
    
    def _extract_documentation(self, tree: ast.AST) -> Dict:
        """Extract documentation from code."""
        docs = {
            'module': ast.get_docstring(tree),
            'classes': {},
            'functions': {}
        }
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                docs['classes'][node.name] = ast.get_docstring(node)
            elif isinstance(node, ast.FunctionDef):
                docs['functions'][node.name] = ast.get_docstring(node)
        
        return docs
    
    def _analyze_complexity(self, tree: ast.AST) -> Dict:
        """Analyze code complexity."""
        metrics = {
            'cyclomatic_complexity': 0,
            'cognitive_complexity': 0,
            'depth': 0
        }
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For)):
                metrics['cyclomatic_complexity'] += 1
            if isinstance(node, ast.Try):
                metrics['cognitive_complexity'] += 1
        
        return {
            'metrics': metrics,
            'score': sum(metrics.values()) / len(metrics)
        }

class MarkdownProcessor(FormatProcessor):
    """Processes markdown content."""
    
    async def process(self, content: str) -> ProcessingResult:
        """Process markdown content."""
        try:
            # Extract structure
            structure = self._analyze_structure(content)
            
            # Extract metadata
            metadata = self._extract_metadata(content)
            
            # Analyze content
            analysis = self._analyze_content(content)
            
            return ProcessingResult(
                content_type='markdown',
                structured_content={
                    'structure': structure,
                    'sections': self._parse_sections(content)
                },
                metadata=metadata,
                analysis=analysis
            )
            
        except Exception as e:
            self.logger.error(f"Markdown processing failed: {str(e)}")
            raise
    
    def validate_format(self, content: str) -> bool:
        """Validate if content is markdown."""
        # Check for common markdown patterns
        patterns = [
            r'^#+ ',  # Headers
            r'^\* ',  # Lists
            r'^- ',   # Lists
            r'`.*`',  # Code
            r'\[.*\]\(.*\)'  # Links
        ]
        return any(re.search(p, content, re.MULTILINE) for p in patterns)
    
    def _analyze_structure(self, content: str) -> Dict:
        """Analyze markdown structure."""
        structure = {
            'headers': [],
            'lists': [],
            'code_blocks': [],
            'links': []
        }
        
        # Extract headers
        structure['headers'] = re.findall(r'^(#+) (.+)$', content, re.MULTILINE)
        
        # Extract lists
        structure['lists'] = re.findall(r'^[\*-] (.+)$', content, re.MULTILINE)
        
        # Extract code blocks
        structure['code_blocks'] = re.findall(r'```[\w]*\n(.*?)```', content, re.DOTALL)
        
        # Extract links
        structure['links'] = re.findall(r'\[(.*?)\]\((.*?)\)', content)
        
        return structure
    
    def _extract_metadata(self, content: str) -> Dict:
        """Extract metadata from markdown."""
        metadata = {
            'title': None,
            'description': None,
            'tags': []
        }
        
        # Try to find title (first h1)
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if title_match:
            metadata['title'] = title_match.group(1)
        
        # Try to find description (first paragraph)
        desc_match = re.search(r'^\n([^#\n].+?)\n\n', content, re.MULTILINE)
        if desc_match:
            metadata['description'] = desc_match.group(1)
        
        return metadata
    
    def _analyze_content(self, content: str) -> Dict:
        """Analyze markdown content."""
        return {
            'readability': self._calculate_readability(content),
            'structure_score': self._calculate_structure_score(content),
            'completeness': self._calculate_completeness(content)
        }
    
    def _parse_sections(self, content: str) -> List[Dict]:
        """Parse markdown into sections."""
        sections = []
        current_section = None
        
        for line in content.split('\n'):
            if line.startswith('#'):
                if current_section:
                    sections.append(current_section)
                level = len(re.match(r'^#+', line).group())
                title = line.lstrip('#').strip()
                current_section = {
                    'level': level,
                    'title': title,
                    'content': []
                }
            elif current_section:
                current_section['content'].append(line)
        
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _calculate_readability(self, content: str) -> float:
        """Calculate content readability score."""
        return 0.85  # Placeholder
    
    def _calculate_structure_score(self, content: str) -> float:
        """Calculate structure quality score."""
        return 0.90  # Placeholder
    
    def _calculate_completeness(self, content: str) -> float:
        """Calculate content completeness score."""
        return 0.95  # Placeholder

class APIProcessor(FormatProcessor):
    """Processes API specification content."""
    
    async def process(self, content: str) -> ProcessingResult:
        """Process API specification content."""
        try:
            # Parse API spec
            spec = self._parse_spec(content)
            
            # Extract endpoints
            endpoints = self._extract_endpoints(spec)
            
            # Analyze API structure
            analysis = self._analyze_api(spec)
            
            return ProcessingResult(
                content_type='api',
                structured_content={
                    'spec': spec,
                    'endpoints': endpoints
                },
                metadata={
                    'version': spec.get('version'),
                    'format': 'openapi'
                },
                analysis=analysis
            )
            
        except Exception as e:
            self.logger.error(f"API spec processing failed: {str(e)}")
            raise
    
    def validate_format(self, content: str) -> bool:
        """Validate if content is API spec."""
        try:
            spec = self._parse_spec(content)
            return 'openapi' in spec or 'swagger' in spec
        except:
            return False
    
    def _parse_spec(self, content: str) -> Dict:
        """Parse API specification."""
        # Placeholder for actual OpenAPI/Swagger parsing
        return {}
    
    def _extract_endpoints(self, spec: Dict) -> List[Dict]:
        """Extract API endpoints from spec."""
        endpoints = []
        # Implementation for endpoint extraction
        return endpoints
    
    def _analyze_api(self, spec: Dict) -> Dict:
        """Analyze API specification."""
        return {
            'complexity': self._calculate_api_complexity(spec),
            'coverage': self._calculate_api_coverage(spec),
            'consistency': self._calculate_api_consistency(spec)
        }
    
    def _calculate_api_complexity(self, spec: Dict) -> float:
        """Calculate API complexity score."""
        return 0.80  # Placeholder
    
    def _calculate_api_coverage(self, spec: Dict) -> float:
        """Calculate API documentation coverage."""
        return 0.85  # Placeholder
    
    def _calculate_api_consistency(self, spec: Dict) -> float:
        """Calculate API consistency score."""
        return 0.90  # Placeholder
