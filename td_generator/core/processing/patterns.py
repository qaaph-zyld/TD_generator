"""
Pattern recognition system for documentation generation.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
import logging
import re
from collections import defaultdict

@dataclass
class Pattern:
    name: str
    description: str
    indicators: List[str]
    weight: float = 1.0

@dataclass
class PatternMatch:
    pattern: Pattern
    confidence: float
    context: Dict
    location: Optional[Dict] = None

class PatternLibrary:
    """Library of documentation patterns."""
    
    def __init__(self):
        self.patterns: Dict[str, Pattern] = {}
        self._initialize_patterns()
    
    def _initialize_patterns(self):
        """Initialize default patterns."""
        self.patterns.update({
            'api_endpoint': Pattern(
                name='API Endpoint',
                description='REST API endpoint documentation pattern',
                indicators=['GET', 'POST', 'PUT', 'DELETE', 'endpoint', 'route'],
                weight=1.0
            ),
            'class_definition': Pattern(
                name='Class Definition',
                description='Object-oriented class documentation pattern',
                indicators=['class', 'method', 'attribute', 'property'],
                weight=0.8
            ),
            'function_definition': Pattern(
                name='Function Definition',
                description='Function or method documentation pattern',
                indicators=['function', 'parameter', 'return', 'raises'],
                weight=0.8
            ),
            'configuration': Pattern(
                name='Configuration',
                description='Configuration or settings documentation pattern',
                indicators=['config', 'setting', 'parameter', 'option'],
                weight=0.6
            ),
            'tutorial': Pattern(
                name='Tutorial',
                description='Step-by-step guide or tutorial pattern',
                indicators=['step', 'guide', 'tutorial', 'example'],
                weight=0.7
            )
        })
    
    def add_pattern(self, pattern: Pattern):
        """Add a new pattern to the library."""
        self.patterns[pattern.name] = pattern
    
    def get_pattern(self, name: str) -> Pattern:
        """Get pattern by name."""
        return self.patterns[name]
    
    def list_patterns(self) -> List[str]:
        """List all available patterns."""
        return list(self.patterns.keys())

class PatternMatcher:
    """Matches patterns in content."""
    
    def __init__(self):
        self.library = PatternLibrary()
        self.logger = logging.getLogger(__name__)
    
    def find_patterns(self, content: str) -> List[PatternMatch]:
        """Find patterns in content."""
        matches = []
        
        for pattern in self.library.patterns.values():
            confidence, context = self._calculate_pattern_confidence(
                content,
                pattern
            )
            
            if confidence > 0.5:  # Confidence threshold
                matches.append(PatternMatch(
                    pattern=pattern,
                    confidence=confidence,
                    context=context,
                    location=self._find_pattern_location(content, pattern)
                ))
        
        return sorted(matches, key=lambda m: m.confidence, reverse=True)
    
    def _calculate_pattern_confidence(self,
                                   content: str,
                                   pattern: Pattern) -> tuple[float, Dict]:
        """Calculate confidence score for pattern match."""
        # Count indicator occurrences
        indicator_counts = defaultdict(int)
        for indicator in pattern.indicators:
            count = len(re.findall(rf'\b{indicator}\b', content, re.IGNORECASE))
            indicator_counts[indicator] = count
        
        # Calculate confidence score
        total_indicators = len(pattern.indicators)
        matched_indicators = sum(1 for count in indicator_counts.values() if count > 0)
        base_confidence = matched_indicators / total_indicators
        
        # Adjust confidence based on indicator frequency
        frequency_factor = sum(indicator_counts.values()) / (len(content.split()) + 1)
        adjusted_confidence = base_confidence * (1 + frequency_factor)
        
        # Normalize confidence to [0, 1]
        final_confidence = min(adjusted_confidence, 1.0)
        
        return final_confidence, {
            'indicator_counts': dict(indicator_counts),
            'frequency_factor': frequency_factor
        }
    
    def _find_pattern_location(self, content: str, pattern: Pattern) -> Dict:
        """Find pattern location in content."""
        locations = {}
        
        for indicator in pattern.indicators:
            matches = list(re.finditer(
                rf'\b{indicator}\b',
                content,
                re.IGNORECASE
            ))
            if matches:
                locations[indicator] = [
                    {'start': m.start(), 'end': m.end()}
                    for m in matches
                ]
        
        return locations if locations else None

class PatternAnalyzer:
    """Analyzes and applies pattern-based recommendations."""
    
    def __init__(self):
        self.matcher = PatternMatcher()
        self.logger = logging.getLogger(__name__)
    
    def analyze_content(self, content: str) -> Dict:
        """Analyze content for patterns and generate recommendations."""
        try:
            # Find patterns
            matches = self.matcher.find_patterns(content)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(matches)
            
            # Calculate pattern coverage
            coverage = self._calculate_pattern_coverage(matches)
            
            return {
                'patterns': [
                    {
                        'name': match.pattern.name,
                        'confidence': match.confidence,
                        'context': match.context
                    }
                    for match in matches
                ],
                'recommendations': recommendations,
                'coverage': coverage
            }
            
        except Exception as e:
            self.logger.error(f"Pattern analysis failed: {str(e)}")
            raise
    
    def _generate_recommendations(self,
                                matches: List[PatternMatch]) -> List[Dict]:
        """Generate recommendations based on pattern matches."""
        recommendations = []
        
        for match in matches:
            if match.confidence > 0.8:
                recommendations.append({
                    'pattern': match.pattern.name,
                    'confidence': match.confidence,
                    'suggestion': self._get_pattern_suggestion(match.pattern)
                })
        
        return recommendations
    
    def _calculate_pattern_coverage(self, matches: List[PatternMatch]) -> float:
        """Calculate pattern coverage score."""
        if not matches:
            return 0.0
        
        total_confidence = sum(match.confidence for match in matches)
        return total_confidence / len(matches)
    
    def _get_pattern_suggestion(self, pattern: Pattern) -> str:
        """Get suggestion for pattern application."""
        suggestions = {
            'api_endpoint': "Consider adding request/response examples",
            'class_definition': "Add attribute type hints and descriptions",
            'function_definition': "Include parameter and return type documentation",
            'configuration': "Provide default values and valid ranges",
            'tutorial': "Add step numbers and expected outcomes"
        }
        return suggestions.get(pattern.name, "Consider adding more details")
