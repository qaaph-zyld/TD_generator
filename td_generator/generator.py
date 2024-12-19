"""
Core module for the TD Generator.
"""
from dataclasses import dataclass
from typing import Dict, Optional
import anthropic
import logging
import yaml

@dataclass
class DocumentationConfig:
    input_type: str  # code/notes/api
    output_format: str  # markdown/html/pdf
    style_guide: Dict
    target_audience: str
    special_requirements: Optional[Dict] = None

class DocumentationGenerator:
    def __init__(self, config_path: str):
        self.config = self._load_config(config_path)
        self.client = anthropic.Client()
        self.logger = self._setup_logging()
        
    def _load_config(self, config_path: str) -> DocumentationConfig:
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        return DocumentationConfig(**config_data)
    
    def _setup_logging(self) -> logging.Logger:
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        return logging.getLogger(__name__)
