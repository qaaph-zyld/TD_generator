"""
Global Market Management System for Worldwide Expansion.
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
import forex_python.converter
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from babel import Locale, numbers, dates

class MarketType(str, Enum):
    """Market types."""
    EMERGING = "emerging"
    DEVELOPING = "developing"
    MATURE = "mature"
    STRATEGIC = "strategic"

class RegionType(str, Enum):
    """Region types."""
    AMERICAS = "americas"
    EMEA = "emea"
    APAC = "apac"
    GLOBAL = "global"

class LocalizationType(str, Enum):
    """Localization types."""
    LANGUAGE = "language"
    CURRENCY = "currency"
    TIMEZONE = "timezone"
    REGULATIONS = "regulations"

@dataclass
class MarketProfile:
    """Market profile definition."""
    id: str
    name: str
    type: MarketType
    region: RegionType
    country_code: str
    language_codes: List[str]
    currency_code: str
    timezone: str
    regulations: Dict[str, Any]
    metrics: Dict[str, float]
    status: str
    created_at: datetime
    updated_at: datetime

@dataclass
class LocalizationConfig:
    """Localization configuration."""
    id: str
    market_id: str
    type: LocalizationType
    settings: Dict[str, Any]
    status: str
    created_at: datetime
    updated_at: datetime

class MarketManager:
    """Manages global market expansion and localization."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.markets: Dict[str, MarketProfile] = {}
        self.localizations: Dict[str, List[LocalizationConfig]] = {}
        self.storage_path = "data/global/markets"
        self._initialize_storage()
        self._load_configuration()
        self.forex = forex_python.converter.CurrencyRates()
        self.geolocator = Nominatim(user_agent="td_generator")
        self.tf = TimezoneFinder()
    
    def _initialize_storage(self):
        """Initialize storage structure."""
        directories = [
            "profiles",
            "localizations",
            "metrics",
            "regulations",
            "reports"
        ]
        
        for directory in directories:
            os.makedirs(
                os.path.join(self.storage_path, directory),
                exist_ok=True
            )
    
    def _load_configuration(self):
        """Load market configuration."""
        config_path = os.path.join(self.storage_path, "config.yaml")
        
        # Create default configuration if none exists
        if not os.path.exists(config_path):
            self._create_default_configuration()
    
    def _create_default_configuration(self):
        """Create default market configuration."""
        default_config = {
            "market_types": [
                {
                    "type": "emerging",
                    "requirements": ["basic_compliance"]
                },
                {
                    "type": "developing",
                    "requirements": ["standard_compliance"]
                },
                {
                    "type": "mature",
                    "requirements": ["advanced_compliance"]
                },
                {
                    "type": "strategic",
                    "requirements": ["full_compliance"]
                }
            ],
            "region_types": [
                {
                    "type": "americas",
                    "countries": ["US", "CA", "BR", "MX"]
                },
                {
                    "type": "emea",
                    "countries": ["GB", "DE", "FR", "AE"]
                },
                {
                    "type": "apac",
                    "countries": ["CN", "JP", "IN", "SG"]
                },
                {
                    "type": "global",
                    "countries": ["*"]
                }
            ],
            "localization_types": [
                {
                    "type": "language",
                    "settings": ["translation", "formatting"]
                },
                {
                    "type": "currency",
                    "settings": ["symbol", "format"]
                },
                {
                    "type": "timezone",
                    "settings": ["format", "dst"]
                },
                {
                    "type": "regulations",
                    "settings": ["privacy", "security"]
                }
            ]
        }
        
        # Save configuration
        config_path = os.path.join(self.storage_path, "config.yaml")
        with open(config_path, 'w') as f:
            yaml.dump(default_config, f)
    
    async def create_market(
        self,
        name: str,
        type: MarketType,
        region: RegionType,
        country_code: str,
        language_codes: List[str],
        currency_code: str
    ) -> MarketProfile:
        """Create market profile."""
        # Validate country code
        country = pycountry.countries.get(alpha_2=country_code.upper())
        if not country:
            raise ValueError(f"Invalid country code: {country_code}")
        
        # Validate language codes
        for code in language_codes:
            if not pycountry.languages.get(alpha_2=code.lower()):
                raise ValueError(f"Invalid language code: {code}")
        
        # Validate currency code
        if not pycountry.currencies.get(alpha_3=currency_code.upper()):
            raise ValueError(f"Invalid currency code: {currency_code}")
        
        # Get timezone
        location = self.geolocator.geocode(country.name)
        timezone = self.tf.timezone_at(
            lat=location.latitude,
            lng=location.longitude
        )
        
        # Create market profile
        profile = MarketProfile(
            id=f"market-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            name=name,
            type=type,
            region=region,
            country_code=country_code.upper(),
            language_codes=[code.lower() for code in language_codes],
            currency_code=currency_code.upper(),
            timezone=timezone,
            regulations=self._get_regulations(type, country_code),
            metrics={},
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.markets[profile.id] = profile
        
        # Save market profile
        self._save_market(profile)
        
        # Create default localizations
        await self._create_default_localizations(profile)
        
        self.logger.info(f"Market created: {profile.id}")
        return profile
    
    def _save_market(self, profile: MarketProfile):
        """Save market profile to storage."""
        profile_path = os.path.join(
            self.storage_path,
            "profiles",
            f"{profile.id}.json"
        )
        
        with open(profile_path, 'w') as f:
            json.dump(vars(profile), f, default=str)
    
    def _get_regulations(
        self,
        type: MarketType,
        country_code: str
    ) -> Dict[str, Any]:
        """Get market regulations."""
        regulations = {
            "privacy": {
                "gdpr": country_code in ["GB", "DE", "FR"],
                "ccpa": country_code == "US",
                "lgpd": country_code == "BR"
            },
            "security": {
                "encryption": "required",
                "data_residency": "recommended",
                "audit_logs": "required"
            },
            "compliance": {
                MarketType.EMERGING: "basic",
                MarketType.DEVELOPING: "standard",
                MarketType.MATURE: "advanced",
                MarketType.STRATEGIC: "full"
            }[type]
        }
        
        return regulations
    
    async def _create_default_localizations(
        self,
        profile: MarketProfile
    ):
        """Create default localizations for market."""
        # Language localization
        for lang_code in profile.language_codes:
            locale = Locale(lang_code)
            await self.create_localization(
                profile.id,
                LocalizationType.LANGUAGE,
                {
                    "code": lang_code,
                    "name": locale.get_display_name(),
                    "date_format": locale.date_formats["short"],
                    "number_format": locale.number_symbols["decimal"]
                }
            )
        
        # Currency localization
        await self.create_localization(
            profile.id,
            LocalizationType.CURRENCY,
            {
                "code": profile.currency_code,
                "symbol": numbers.get_currency_symbol(
                    profile.currency_code,
                    locale=profile.language_codes[0]
                ),
                "format": numbers.get_currency_format(
                    locale=profile.language_codes[0]
                )
            }
        )
        
        # Timezone localization
        await self.create_localization(
            profile.id,
            LocalizationType.TIMEZONE,
            {
                "zone": profile.timezone,
                "format": "24h" if profile.region == RegionType.EMEA else "12h",
                "dst": True
            }
        )
        
        # Regulations localization
        await self.create_localization(
            profile.id,
            LocalizationType.REGULATIONS,
            profile.regulations
        )
    
    async def create_localization(
        self,
        market_id: str,
        type: LocalizationType,
        settings: Dict[str, Any]
    ) -> LocalizationConfig:
        """Create localization configuration."""
        config = LocalizationConfig(
            id=f"local-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            market_id=market_id,
            type=type,
            settings=settings,
            status="active",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        if market_id not in self.localizations:
            self.localizations[market_id] = []
        
        self.localizations[market_id].append(config)
        
        # Save localization
        self._save_localization(config)
        
        self.logger.info(f"Localization created: {config.id}")
        return config
    
    def _save_localization(self, config: LocalizationConfig):
        """Save localization to storage."""
        config_path = os.path.join(
            self.storage_path,
            "localizations",
            f"{config.id}.json"
        )
        
        with open(config_path, 'w') as f:
            json.dump(vars(config), f, default=str)
    
    def format_currency(
        self,
        amount: float,
        from_currency: str,
        to_currency: str,
        locale: str
    ) -> str:
        """Format currency amount."""
        # Convert amount
        rate = self.forex.get_rate(from_currency, to_currency)
        converted = amount * rate
        
        # Format according to locale
        return numbers.format_currency(
            converted,
            to_currency,
            locale=locale
        )
    
    def format_date(
        self,
        date: datetime,
        locale: str,
        format: str = "short"
    ) -> str:
        """Format date according to locale."""
        return dates.format_date(
            date,
            format=format,
            locale=locale
        )
    
    def format_number(
        self,
        number: float,
        locale: str,
        decimal_places: int = 2
    ) -> str:
        """Format number according to locale."""
        return numbers.format_decimal(
            number,
            locale=locale,
            decimal_quantization=False,
            format=f"#,##0.{'0' * decimal_places}"
        )
    
    def get_market_stats(
        self,
        type: Optional[MarketType] = None,
        region: Optional[RegionType] = None
    ) -> Dict[str, Any]:
        """Get market statistics."""
        markets = self.markets.values()
        
        if type:
            markets = [m for m in markets if m.type == type]
        
        if region:
            markets = [m for m in markets if m.region == region]
        
        if not markets:
            return {
                "total": 0,
                "by_type": {},
                "by_region": {},
                "by_status": {}
            }
        
        return {
            "total": len(markets),
            "by_type": {
                type: len([
                    m for m in markets
                    if m.type == type
                ])
                for type in {m.type for m in markets}
            },
            "by_region": {
                region: len([
                    m for m in markets
                    if m.region == region
                ])
                for region in {m.region for m in markets}
            },
            "by_status": {
                status: len([
                    m for m in markets
                    if m.status == status
                ])
                for status in {m.status for m in markets}
            }
        }
    
    def get_localization_stats(
        self,
        market_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get localization statistics."""
        if market_id:
            localizations = self.localizations.get(market_id, [])
        else:
            localizations = []
            for configs in self.localizations.values():
                localizations.extend(configs)
        
        if not localizations:
            return {
                "total": 0,
                "by_type": {},
                "by_status": {},
                "coverage": {}
            }
        
        return {
            "total": len(localizations),
            "by_type": {
                type: len([
                    l for l in localizations
                    if l.type == type
                ])
                for type in {l.type for l in localizations}
            },
            "by_status": {
                status: len([
                    l for l in localizations
                    if l.status == status
                ])
                for status in {l.status for l in localizations}
            },
            "coverage": {
                market_id: len(configs)
                for market_id, configs in self.localizations.items()
            }
        }
    
    def get_status(self) -> Dict[str, Any]:
        """Get market manager status."""
        return {
            "markets": self.get_market_stats(),
            "localizations": self.get_localization_stats(),
            "health_summary": {
                "market_health": all(
                    market.status == "active"
                    for market in self.markets.values()
                ),
                "localization_health": all(
                    config.status == "active"
                    for configs in self.localizations.values()
                    for config in configs
                ),
                "forex_health": bool(self.forex)
            }
        }
