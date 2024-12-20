"""
Cultural Adaptation System for Global Content and Interface.
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import logging
import json
import os
from pathlib import Path
import yaml
import asyncio
from enum import Enum
import pycountry
from babel import Locale, support
from deep_translator import GoogleTranslator
import langdetect
import emoji
import colorama
from colour import Color

class ContentType(str, Enum):
    """Content types."""
    TEXT = "text"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"

class AdaptationType(str, Enum):
    """Adaptation types."""
    LANGUAGE = "language"
    VISUAL = "visual"
    INTERACTION = "interaction"
    CULTURAL = "cultural"

class PreferenceType(str, Enum):
    """Preference types."""
    COLOR = "color"
    LAYOUT = "layout"
    STYLE = "style"
    BEHAVIOR = "behavior"

@dataclass
class ContentProfile:
    """Content profile definition."""
    id: str
    name: str
    type: ContentType
    source_language: str
    target_languages: List[str]
    adaptations: Dict[str, Any]
    preferences: Dict[str, Any]
    metrics: Dict[str, float]
    status: str
    created_at: datetime
    updated_at: datetime

@dataclass
class AdaptationConfig:
    """Adaptation configuration."""
    id: str
    content_id: str
    type: AdaptationType
    settings: Dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime

class CulturalAdapter:
    """Manages cultural adaptation and localization."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.contents: Dict[str, ContentProfile] = {}
        self.adaptations: Dict[str, List[AdaptationConfig]] = {}
        self.storage_path = "data/global/cultural"
        self._initialize_storage()
        self._load_configuration()
        self.translators: Dict[str, GoogleTranslator] = {}
    
    def _initialize_storage(self):
        """Initialize storage structure."""
        directories = [
            "profiles",
            "adaptations",
            "resources",
            "preferences",
            "reports"
        ]
        
        for directory in directories:
            os.makedirs(
                os.path.join(self.storage_path, directory),
                exist_ok=True
            )
    
    def _load_configuration(self):
        """Load cultural configuration."""
        config_path = os.path.join(self.storage_path, "config.yaml")
        
        # Create default configuration if none exists
        if not os.path.exists(config_path):
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default cultural configuration."""
        default_config = {
            "content_types": [
                {
                    "type": "text",
                    "adaptations": ["translation", "formatting"]
                },
                {
                    "type": "image",
                    "adaptations": ["colors", "symbols"]
                },
                {
                    "type": "video",
                    "adaptations": ["subtitles", "dubbing"]
                },
                {
                    "type": "audio",
                    "adaptations": ["transcription", "dubbing"]
                }
            ],
            "adaptation_types": [
                {
                    "type": "language",
                    "settings": ["translation", "tone"]
                },
                {
                    "type": "visual",
                    "settings": ["colors", "layout"]
                },
                {
                    "type": "interaction",
                    "settings": ["gestures", "feedback"]
                },
                {
                    "type": "cultural",
                    "settings": ["customs", "values"]
                }
            ],
            "preference_types": [
                {
                    "type": "color",
                    "options": ["theme", "contrast"]
                },
                {
                    "type": "layout",
                    "options": ["direction", "density"]
                },
                {
                    "type": "style",
                    "options": ["formal", "casual"]
                },
                {
                    "type": "behavior",
                    "options": ["feedback", "guidance"]
                }
            ],
            "cultural_preferences": {
                "colors": {
                    "cn": {"lucky": "red", "mourning": "white"},
                    "jp": {"formal": "black", "casual": "pastels"},
                    "in": {"festive": "orange", "spiritual": "saffron"}
                },
                "layouts": {
                    "ar": {"direction": "rtl", "density": "spacious"},
                    "jp": {"alignment": "center", "density": "compact"},
                    "us": {"direction": "ltr", "density": "balanced"}
                },
                "interactions": {
                    "jp": {"feedback": "subtle", "guidance": "implicit"},
                    "us": {"feedback": "direct", "guidance": "explicit"},
                    "de": {"feedback": "precise", "guidance": "structured"}
                }
            }
        }
        
        # Save configuration
        config_path = os.path.join(self.storage_path, "config.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f)
    
    async def create_content(
        self,
        name: str,
        type: ContentType,
        source_language: str,
        target_languages: List[str],
        preferences: Dict[str, Any]
    ) -> ContentProfile:
        """Create content profile."""
        # Validate languages
        if not pycountry.languages.get(alpha_2=source_language.lower()):
            raise ValueError(f"Invalid source language: {source_language}")
        
        for lang in target_languages:
            if not pycountry.languages.get(alpha_2=lang.lower()):
                raise ValueError(f"Invalid target language: {lang}")
        
        # Create content profile
        profile = ContentProfile(
            id=f"content-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=name,
            type=type,
            source_language=source_language.lower(),
            target_languages=[lang.lower() for lang in target_languages],
            adaptations={},
            preferences=preferences,
            metrics={},
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.contents[profile.id] = profile
        
        # Save content profile
        self._save_content(profile)
        
        # Create default adaptations
        await self._create_default_adaptations(profile)
        
        self.logger.info(f"Content created: {profile.id}")
        return profile
    
    def _save_content(self, profile: ContentProfile):
        """Save content profile to storage."""
        profile_path = os.path.join(
            self.storage_path,
            "profiles",
            f"{profile.id}.json"
        )
        
        with open(profile_path, 'w') as f:
            json.dump(vars(profile), f, default=str)
    
    async def _create_default_adaptations(
        self,
        profile: ContentProfile
    ):
        """Create default adaptations for content."""
        # Language adaptation
        for lang in profile.target_languages:
            await self.create_adaptation(
                profile.id,
                AdaptationType.LANGUAGE,
                {
                    "source": profile.source_language,
                    "target": lang,
                    "tone": "formal",
                    "context": "business"
                }
            )
        
        # Visual adaptation
        await self.create_adaptation(
            profile.id,
            AdaptationType.VISUAL,
            {
                "colors": self._get_color_preferences(
                    profile.target_languages[0]
                ),
                "layout": self._get_layout_preferences(
                    profile.target_languages[0]
                )
            }
        )
        
        # Interaction adaptation
        await self.create_adaptation(
            profile.id,
            AdaptationType.INTERACTION,
            {
                "feedback": self._get_interaction_preferences(
                    profile.target_languages[0],
                    "feedback"
                ),
                "guidance": self._get_interaction_preferences(
                    profile.target_languages[0],
                    "guidance"
                )
            }
        )
        
        # Cultural adaptation
        await self.create_adaptation(
            profile.id,
            AdaptationType.CULTURAL,
            {
                "customs": self._get_cultural_preferences(
                    profile.target_languages[0],
                    "customs"
                ),
                "values": self._get_cultural_preferences(
                    profile.target_languages[0],
                    "values"
                )
            }
        )
    
    def _get_color_preferences(self, language: str) -> Dict[str, str]:
        """Get color preferences for language."""
        config_path = os.path.join(self.storage_path, "config.yaml")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        return config["cultural_preferences"]["colors"].get(
            language,
            {"primary": "#000000", "secondary": "#FFFFFF"}
        )
    
    def _get_layout_preferences(self, language: str) -> Dict[str, str]:
        """Get layout preferences for language."""
        config_path = os.path.join(self.storage_path, "config.yaml")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        return config["cultural_preferences"]["layouts"].get(
            language,
            {"direction": "ltr", "density": "balanced"}
        )
    
    def _get_interaction_preferences(
        self,
        language: str,
        type: str
    ) -> str:
        """Get interaction preferences for language."""
        config_path = os.path.join(self.storage_path, "config.yaml")
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        prefs = config["cultural_preferences"]["interactions"].get(
            language,
            {"feedback": "direct", "guidance": "explicit"}
        )
        
        return prefs.get(type, "default")
    
    def _get_cultural_preferences(
        self,
        language: str,
        type: str
    ) -> Dict[str, Any]:
        """Get cultural preferences for language."""
        # This would typically come from a cultural database
        preferences = {
            "customs": {
                "jp": {
                    "formality": "high",
                    "hierarchy": "strict"
                },
                "us": {
                    "formality": "low",
                    "hierarchy": "flexible"
                }
            },
            "values": {
                "jp": {
                    "group": "collective",
                    "communication": "indirect"
                },
                "us": {
                    "group": "individual",
                    "communication": "direct"
                }
            }
        }
        
        return preferences[type].get(
            language,
            {"style": "neutral", "tone": "balanced"}
        )
    
    async def create_adaptation(
        self,
        content_id: str,
        type: AdaptationType,
        settings: Dict[str, Any]
    ) -> AdaptationConfig:
        """Create adaptation configuration."""
        config = AdaptationConfig(
            id=f"adapt-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            content_id=content_id,
            type=type,
            settings=settings,
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        if content_id not in self.adaptations:
            self.adaptations[content_id] = []
        
        self.adaptations[content_id].append(config)
        
        # Save adaptation
        self._save_adaptation(config)
        
        self.logger.info(f"Adaptation created: {config.id}")
        return config
    
    def _save_adaptation(self, config: AdaptationConfig):
        """Save adaptation to storage."""
        config_path = os.path.join(
            self.storage_path,
            "adaptations",
            f"{config.id}.json"
        )
        
        with open(config_path, 'w') as f:
            json.dump(vars(config), f, default=str)
    
    def translate_text(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """Translate text between languages."""
        key = f"{source_lang}-{target_lang}"
        if key not in self.translators:
            self.translators[key] = GoogleTranslator(
                source=source_lang,
                target=target_lang
            )
        
        return self.translators[key].translate(text)
    
    def adapt_colors(
        self,
        colors: List[str],
        target_lang: str
    ) -> List[str]:
        """Adapt colors for target culture."""
        preferences = self._get_color_preferences(target_lang)
        adapted = []
        
        for color in colors:
            # Convert color to Color object
            c = Color(color)
            
            # Adapt based on preferences
            if target_lang in ["cn", "in"]:
                # Increase saturation for Asian markets
                c.saturation = min(c.saturation * 1.2, 1.0)
            elif target_lang in ["de", "se"]:
                # Decrease saturation for Northern European markets
                c.saturation = max(c.saturation * 0.8, 0.0)
            
            adapted.append(c.hex)
        
        return adapted
    
    def adapt_layout(
        self,
        layout: Dict[str, Any],
        target_lang: str
    ) -> Dict[str, Any]:
        """Adapt layout for target culture."""
        preferences = self._get_layout_preferences(target_lang)
        adapted = layout.copy()
        
        # Adapt text direction
        adapted["direction"] = preferences["direction"]
        
        # Adapt spacing
        if preferences["density"] == "compact":
            adapted["spacing"] = "condensed"
        elif preferences["density"] == "spacious":
            adapted["spacing"] = "expanded"
        else:
            adapted["spacing"] = "normal"
        
        return adapted
    
    def adapt_interaction(
        self,
        interaction: Dict[str, Any],
        target_lang: str
    ) -> Dict[str, Any]:
        """Adapt interaction for target culture."""
        feedback = self._get_interaction_preferences(
            target_lang,
            "feedback"
        )
        guidance = self._get_interaction_preferences(
            target_lang,
            "guidance"
        )
        
        adapted = interaction.copy()
        adapted["feedback_style"] = feedback
        adapted["guidance_style"] = guidance
        
        return adapted
    
    def get_content_stats(
        self,
        type: Optional[ContentType] = None
    ) -> Dict[str, Any]:
        """Get content statistics."""
        contents = self.contents.values()
        
        if type:
            contents = [c for c in contents if c.type == type]
        
        if not contents:
            return {
                "total": 0,
                "by_type": {},
                "by_language": {},
                "by_status": {}
            }
        
        return {
            "total": len(contents),
            "by_type": {
                type: len([
                    c for c in contents
                    if c.type == type
                ])
                for type in {c.type for c in contents}
            },
            "by_language": {
                lang: len([
                    c for c in contents
                    if lang in c.target_languages
                ])
                for lang in set().union(
                    *[c.target_languages for c in contents]
                )
            },
            "by_status": {
                status: len([
                    c for c in contents
                    if c.status == status
                ])
                for status in {c.status for c in contents}
            }
        }
    
    def get_adaptation_stats(
        self,
        content_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get adaptation statistics."""
        if content_id:
            adaptations = self.adaptations.get(content_id, [])
        else:
            adaptations = []
            for configs in self.adaptations.values():
                adaptations.extend(configs)
        
        if not adaptations:
            return {
                "total": 0,
                "by_type": {},
                "by_status": {},
                "coverage": {}
            }
        
        return {
            "total": len(adaptations),
            "by_type": {
                type: len([
                    a for a in adaptations
                    if a.type == type
                ])
                for type in {a.type for a in adaptations}
            },
            "by_status": {
                status: len([
                    a for a in adaptations
                    if a.status == status
                ])
                for status in {a.status for a in adaptations}
            },
            "coverage": {
                content_id: len(configs)
                for content_id, configs in self.adaptations.items()
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get cultural adapter status."""
        return {
            "contents": self.get_content_stats(),
            "adaptations": self.get_adaptation_stats(),
            "health_summary": {
                "content_health": all(
                    content.status == "active"
                    for content in self.contents.values()
                ),
                "adaptation_health": all(
                    config.status == "active"
                    for configs in self.adaptations.values()
                    for config in configs
                ),
                "translator_health": bool(self.translators)
            }
        }
