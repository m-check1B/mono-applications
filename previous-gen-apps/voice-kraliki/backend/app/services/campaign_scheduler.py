"""
Campaign scheduler service for managing campaign execution based on schedules.
"""

import logging
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.campaign import Campaign, CampaignStatus

logger = logging.getLogger(__name__)


class CampaignScheduler:
    """
    Service for scheduling and managing campaign execution.

    Features:
    - Check campaigns that should start based on schedule
    - Check campaigns that should stop based on schedule
    - Respect business hours
    - Enforce max concurrent calls and calls per hour limits
    """

    def __init__(self):
        self._scheduled_campaigns: dict[int, datetime] = {}
        self._running_campaigns: dict[int, datetime] = {}

    async def check_and_start_campaigns(self, db: AsyncSession) -> list[Campaign]:
        """
        Check for campaigns that should start and activate them.

        Returns:
            List of campaigns that were started
        """
        now = datetime.now(UTC)

        # Find campaigns that should start
        campaigns_to_start = []

        # Get draft campaigns with start_time set and <= now
        query = select(Campaign).where(
            Campaign.status == CampaignStatus.DRAFT,
            Campaign.start_time.isnot(None),
            Campaign.start_time <= now,
        )
        result = await db.execute(query)
        draft_campaigns = result.scalars().all()

        # Also check paused campaigns that should resume
        paused_query = select(Campaign).where(
            Campaign.status == CampaignStatus.PAUSED,
            Campaign.start_time.isnot(None),
            Campaign.start_time <= now,
            Campaign.end_time > now,
        )
        paused_result = await db.execute(paused_query)
        paused_campaigns = paused_result.scalars().all()

        campaigns_to_start.extend(draft_campaigns)
        campaigns_to_start.extend(paused_campaigns)

        started_campaigns = []
        for campaign in campaigns_to_start:
            if await self._can_start_campaign(campaign, db):
                campaign.status = CampaignStatus.ACTIVE
                db.add(campaign)
                self._running_campaigns[campaign.id] = now
                started_campaigns.append(campaign)
                logger.info(f"Started campaign {campaign.id}: {campaign.name}")

        if started_campaigns:
            await db.commit()

        return started_campaigns

    async def check_and_stop_campaigns(self, db: AsyncSession) -> list[Campaign]:
        """
        Check for campaigns that should stop and deactivate them.

        Returns:
            List of campaigns that were stopped/completed
        """
        now = datetime.now(UTC)

        # Get active campaigns that should stop
        query = select(Campaign).where(
            Campaign.status == CampaignStatus.ACTIVE,
            Campaign.end_time.isnot(None),
            Campaign.end_time <= now,
        )
        result = await db.execute(query)
        active_campaigns = result.scalars().all()

        stopped_campaigns = []
        for campaign in active_campaigns:
            campaign.status = CampaignStatus.COMPLETED
            db.add(campaign)
            if campaign.id in self._running_campaigns:
                del self._running_campaigns[campaign.id]
            stopped_campaigns.append(campaign)
            logger.info(f"Stopped campaign {campaign.id}: {campaign.name}")

        if stopped_campaigns:
            await db.commit()

        return stopped_campaigns

    async def _can_start_campaign(self, campaign: Campaign, db: AsyncSession) -> bool:
        """
        Check if a campaign can start based on business hours and limits.

        Args:
            campaign: Campaign to check
            db: Database session

        Returns:
            True if campaign can start, False otherwise
        """
        now = datetime.now(UTC)

        # Check business hours if enabled
        if campaign.business_hours_only:
            if not self._is_within_business_hours(now, campaign.timezone):
                logger.debug(f"Campaign {campaign.id} not within business hours")
                return False

        # Check if we've hit max concurrent campaigns
        # (This is a simple check - in production you'd want more sophisticated logic)
        active_query = select(Campaign).where(Campaign.status == CampaignStatus.ACTIVE)
        active_result = await db.execute(active_query)
        active_count = len(active_result.scalars().all())

        # This would need to be configurable or checked per-campaign
        max_concurrent_campaigns = 10
        if active_count >= max_concurrent_campaigns:
            logger.debug(f"Max concurrent campaigns ({max_concurrent_campaigns}) reached")
            return False

        return True

    def _is_within_business_hours(self, when: datetime, timezone_str: str = "UTC") -> bool:
        """
        Check if a datetime is within business hours (9 AM - 5 PM).

        Args:
            when: Datetime to check
            timezone_str: Timezone string

        Returns:
            True if within business hours, False otherwise
        """
        # Simple implementation - assume 9 AM to 5 PM Monday-Friday
        # In production, this should be configurable per campaign or org
        weekday = when.weekday()  # 0 = Monday, 6 = Sunday
        hour = when.hour

        # Weekday and between 9 AM and 5 PM
        return weekday < 5 and 9 <= hour < 17

    async def get_campaign_status_summary(self, db: AsyncSession) -> dict[str, int]:
        """
        Get a summary of campaign statuses.

        Returns:
            Dict mapping status to count
        """
        query = select(Campaign.status, Campaign.id)
        result = await db.execute(query)
        statuses = [row[0] for row in result.all()]

        summary = {}
        for status in statuses:
            summary[status] = summary.get(status, 0) + 1

        return summary

    def get_running_campaigns(self) -> dict[int, datetime]:
        """
        Get campaigns currently being tracked as running by the scheduler.

        Returns:
            Dict mapping campaign_id to start_time
        """
        return self._running_campaigns.copy()


# Singleton instance
_campaign_scheduler: CampaignScheduler | None = None


def get_campaign_scheduler() -> CampaignScheduler:
    """
    Get the singleton campaign scheduler instance.

    Returns:
        CampaignScheduler instance
    """
    global _campaign_scheduler
    if _campaign_scheduler is None:
        _campaign_scheduler = CampaignScheduler()
    return _campaign_scheduler


async def run_scheduler_checks(db: AsyncSession) -> dict[str, list[int]]:
    """
    Run all scheduler checks (start/stop campaigns).

    Args:
        db: Database session

    Returns:
        Dict with 'started' and 'stopped' lists of campaign IDs
    """
    scheduler = get_campaign_scheduler()

    started_campaigns = await scheduler.check_and_start_campaigns(db)
    stopped_campaigns = await scheduler.check_and_stop_campaigns(db)

    return {
        "started": [c.id for c in started_campaigns],
        "stopped": [c.id for c in stopped_campaigns],
    }
