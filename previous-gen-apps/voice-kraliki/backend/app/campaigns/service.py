"""
Campaign service for loading and managing call campaign scripts.
"""

import json
import logging
from pathlib import Path

from .models import Campaign, CampaignType

logger = logging.getLogger(__name__)


class CampaignService:
    """Service for managing campaign scripts and execution."""

    def __init__(self, scripts_directory: str | None = None):
        """Initialize the campaign service.
        
        Args:
            scripts_directory: Path to the directory containing campaign JSON files.
                              If None, uses the default scripts directory.
        """
        if scripts_directory is None:
            # Default to the scripts directory relative to this file
            current_dir = Path(__file__).parent
            self.scripts_directory = current_dir / "scripts"
        else:
            self.scripts_directory = Path(scripts_directory)

        self._campaigns_cache: dict[int, Campaign] = {}
        self._campaigns_loaded = False

    def _load_campaigns_from_disk(self) -> dict[int, Campaign]:
        """Load all campaign JSON files from the scripts directory.
        
        Returns:
            Dictionary mapping campaign IDs to Campaign objects.
        """
        campaigns = {}

        if not self.scripts_directory.exists():
            logger.warning("Scripts directory not found: %s", self.scripts_directory)
            return campaigns

        # Load all JSON files in the scripts directory
        for file_path in self.scripts_directory.glob("*.json"):
            try:
                with open(file_path, encoding='utf-8') as f:
                    campaign_data = json.load(f)

                # Parse the campaign using Pydantic model
                campaign = Campaign(**campaign_data)
                campaigns[campaign.id] = campaign

                logger.info("Loaded campaign: %s (ID: %s)", campaign.title, campaign.id)

            except Exception as e:
                logger.error("Error loading campaign from %s: %s", file_path, e)
                continue

        return campaigns

    def _ensure_campaigns_loaded(self):
        """Ensure campaigns are loaded from disk."""
        if not self._campaigns_loaded:
            self._campaigns_cache = self._load_campaigns_from_disk()
            self._campaigns_loaded = True

    def get_campaign(self, campaign_id: int) -> Campaign | None:
        """Get a campaign by ID.
        
        Args:
            campaign_id: The ID of the campaign to retrieve.
            
        Returns:
            The Campaign object if found, None otherwise.
        """
        self._ensure_campaigns_loaded()
        return self._campaigns_cache.get(campaign_id)

    def get_all_campaigns(self) -> list[Campaign]:
        """Get all campaigns.
        
        Returns:
            List of all Campaign objects.
        """
        self._ensure_campaigns_loaded()
        return list(self._campaigns_cache.values())

    def get_campaigns_by_type(self, campaign_type: CampaignType) -> list[Campaign]:
        """Get campaigns by type.
        
        Args:
            campaign_type: The type of campaigns to retrieve.
            
        Returns:
            List of Campaign objects of the specified type.
        """
        self._ensure_campaigns_loaded()
        return [
            campaign for campaign in self._campaigns_cache.values()
            if campaign.type == campaign_type
        ]

    def get_campaigns_by_language(self, language: str) -> list[Campaign]:
        """Get campaigns by language.
        
        Args:
            language: The language code (e.g., 'en', 'es', 'cz').
            
        Returns:
            List of Campaign objects in the specified language.
        """
        self._ensure_campaigns_loaded()
        return [
            campaign for campaign in self._campaigns_cache.values()
            if campaign.language == language
        ]

    def get_campaigns_by_category(self, category: str) -> list[Campaign]:
        """Get campaigns by category.
        
        Args:
            category: The category of campaigns to retrieve.
            
        Returns:
            List of Campaign objects in the specified category.
        """
        self._ensure_campaigns_loaded()
        return [
            campaign for campaign in self._campaigns_cache.values()
            if campaign.category == category
        ]

    def search_campaigns(self, query: str) -> list[Campaign]:
        """Search campaigns by title or campaign name.
        
        Args:
            query: Search query string.
            
        Returns:
            List of Campaign objects matching the search query.
        """
        self._ensure_campaigns_loaded()
        query_lower = query.lower()

        return [
            campaign for campaign in self._campaigns_cache.values()
            if (query_lower in campaign.title.lower() or
                query_lower in campaign.campaign.lower())
        ]

    def reload_campaigns(self):
        """Force reload of all campaigns from disk."""
        self._campaigns_cache = {}
        self._campaigns_loaded = False
        self._ensure_campaigns_loaded()

    def get_campaign_summary(self) -> dict[str, int]:
        """Get a summary of available campaigns.
        
        Returns:
            Dictionary with campaign statistics.
        """
        self._ensure_campaigns_loaded()

        summary = {
            "total": len(self._campaigns_cache),
            "outbound": 0,
            "inbound": 0,
            "languages": {},
            "categories": {}
        }

        for campaign in self._campaigns_cache.values():
            # Count by type
            if campaign.type == CampaignType.OUTBOUND:
                summary["outbound"] += 1
            else:
                summary["inbound"] += 1

            # Count by language
            lang = campaign.language
            summary["languages"][lang] = summary["languages"].get(lang, 0) + 1

            # Count by category
            cat = campaign.category
            summary["categories"][cat] = summary["categories"].get(cat, 0) + 1

        return summary
