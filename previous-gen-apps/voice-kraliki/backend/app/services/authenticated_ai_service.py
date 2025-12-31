"""Authenticated AI Service - AI services with authentication integration.

This module provides authentication-aware AI services that:
- Integrate with the JWT authentication system
- Provide role-based access to AI capabilities
- Track AI usage by user and organization
- Enforce usage limits and permissions
- Audit AI interactions for compliance
"""

import logging
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from app.auth.jwt_auth import UserRole
from app.models.user import User
from app.services.agent_assistance_service import AgentAssistanceService
from app.services.ai_insights import AIInsightsService
from app.services.ai_service_manager import AIServiceManager, ProviderType
from app.services.alerting import AlertingService
from app.services.analytics_service import AnalyticsService
from app.services.audio_quality_optimizer import AudioQualityOptimizer
from app.services.call_artifacts import CallArtifactsService
from app.services.compliance import ComplianceService
from app.services.context_sharing import context_sharing_service
from app.services.provider_health_monitor import ProviderHealthMonitor
from app.services.sentiment_service import SentimentService
from app.services.streaming_tts import get_tts_manager
from app.services.summarization_service import SummarizationService
from app.services.transcription_service import TranscriptionService
from app.services.workflow_automation import WorkflowAutomationService

logger = logging.getLogger(__name__)


class AIServicePermission(str, Enum):
    """Permissions for AI service access."""
    INSIGHTS_READ = "ai:insights:read"
    INSIGHTS_WRITE = "ai:insights:write"
    SENTIMENT_ANALYSIS = "ai:sentiment:analyze"
    TRANSCRIPTION = "ai:transcription:use"
    TTS = "ai:tts:use"
    SUMMARIZATION = "ai:summarization:use"
    AGENT_ASSISTANCE = "ai:agent_assistance:use"
    ANALYTICS = "ai:analytics:read"
    WORKFLOW_AUTOMATION = "ai:workflow:use"
    COMPLIANCE_CHECK = "ai:compliance:check"
    CONTEXT_SHARING = "ai:context:share"
    AUDIO_OPTIMIZATION = "ai:audio:optimize"
    HEALTH_MONITORING = "ai:health:monitor"


class AuthenticatedAIService:
    """Authentication-aware AI service orchestrator.
    
    This service provides secure access to AI capabilities with:
    - User authentication and authorization
    - Role-based access control
    - Usage tracking and auditing
    - Rate limiting and quota management
    """

    def __init__(self):
        """Initialize the authenticated AI service."""
        self.ai_manager = AIServiceManager()
        self.insights_service = AIInsightsService()
        self.sentiment_service = SentimentService()
        self.summarization_service = SummarizationService()
        self.agent_assistance = AgentAssistanceService()
        self.transcription_service = TranscriptionService()
        self.tts_service = get_tts_manager()
        self.analytics_service = AnalyticsService()
        self.call_artifacts = CallArtifactsService()
        self.workflow_automation = WorkflowAutomationService()
        self.compliance_service = ComplianceService()
        self.alerting_service = AlertingService()
        self.context_sharing = context_sharing_service
        self.audio_optimizer = AudioQualityOptimizer()
        self.health_monitor = ProviderHealthMonitor()

        # Usage tracking
        self.usage_tracker: dict[str, dict[str, Any]] = {}

        logger.info("Authenticated AI Service initialized with 15 AI services")

    def _check_permission(self, user: User, permission: AIServicePermission) -> bool:
        """Check if user has permission for AI service.
        
        Args:
            user: User object
            permission: Required permission
            
        Returns:
            True if user has permission
        """
        # Admin has access to everything
        if user.role == UserRole.ADMIN:
            return True

        # Check role-based permissions
        role_permissions = {
            UserRole.AGENT: [
                AIServicePermission.TRANSCRIPTION,
                AIServicePermission.TTS,
                AIServicePermission.SENTIMENT_ANALYSIS,
                AIServicePermission.INSIGHTS_READ,
                AIServicePermission.AGENT_ASSISTANCE,
                AIServicePermission.CONTEXT_SHARING,
                AIServicePermission.AUDIO_OPTIMIZATION,
            ],
            UserRole.SUPERVISOR: [
                AIServicePermission.TRANSCRIPTION,
                AIServicePermission.TTS,
                AIServicePermission.SENTIMENT_ANALYSIS,
                AIServicePermission.INSIGHTS_READ,
                AIServicePermission.INSIGHTS_WRITE,
                AIServicePermission.AGENT_ASSISTANCE,
                AIServicePermission.SUMMARIZATION,
                AIServicePermission.ANALYTICS,
                AIServicePermission.CONTEXT_SHARING,
                AIServicePermission.AUDIO_OPTIMIZATION,
                AIServicePermission.COMPLIANCE_CHECK,
            ],
            UserRole.ANALYST: [
                AIServicePermission.INSIGHTS_READ,
                AIServicePermission.SENTIMENT_ANALYSIS,
                AIServicePermission.TRANSCRIPTION,
                AIServicePermission.SUMMARIZATION,
                AIServicePermission.ANALYTICS,
                AIServicePermission.COMPLIANCE_CHECK,
            ],
        }

        return permission in role_permissions.get(user.role, [])

    def _track_usage(self, user_id: str, service: str, action: str, metadata: dict[str, Any] = None):
        """Track AI service usage for auditing and billing.
        
        Args:
            user_id: User identifier
            service: Service name
            action: Action performed
            metadata: Additional metadata
        """
        if user_id not in self.usage_tracker:
            self.usage_tracker[user_id] = {
                "total_requests": 0,
                "services": {},
                "first_used": datetime.now(UTC),
                "last_used": datetime.now(UTC),
            }

        user_usage = self.usage_tracker[user_id]
        user_usage["total_requests"] += 1
        user_usage["last_used"] = datetime.now(UTC)

        if service not in user_usage["services"]:
            user_usage["services"][service] = {
                "requests": 0,
                "actions": {},
            }

        service_usage = user_usage["services"][service]
        service_usage["requests"] += 1

        if action not in service_usage["actions"]:
            service_usage["actions"][action] = 0
        service_usage["actions"][action] += 1

        if metadata:
            service_usage["last_metadata"] = metadata

        logger.debug(f"Tracked usage: user={user_id}, service={service}, action={action}")

    async def get_ai_insights(
        self,
        user: User,
        conversation_data: dict[str, Any],
        real_time: bool = False
    ) -> dict[str, Any]:
        """Get AI-powered conversation insights.
        
        Args:
            user: Authenticated user
            conversation_data: Conversation data to analyze
            real_time: Whether to provide real-time insights
            
        Returns:
            AI insights and recommendations
        """
        if not self._check_permission(user, AIServicePermission.INSIGHTS_READ):
            raise PermissionError("User lacks permission for AI insights")

        try:
            insights = await self.insights_service.analyze_conversation(
                conversation_data, real_time=real_time
            )

            self._track_usage(
                user.id,
                "ai_insights",
                "analyze_conversation",
                {"real_time": real_time, "data_size": len(str(conversation_data))}
            )

            return insights

        except Exception as e:
            logger.error(f"AI insights failed for user {user.id}: {e}")
            raise

    async def analyze_sentiment(
        self,
        user: User,
        text: str,
        context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Analyze sentiment of text.
        
        Args:
            user: Authenticated user
            text: Text to analyze
            context: Additional context
            
        Returns:
            Sentiment analysis results
        """
        if not self._check_permission(user, AIServicePermission.SENTIMENT_ANALYSIS):
            raise PermissionError("User lacks permission for sentiment analysis")

        try:
            sentiment = await self.sentiment_service.analyze_sentiment(text, context)

            self._track_usage(
                user.id,
                "sentiment_analysis",
                "analyze_text",
                {"text_length": len(text), "has_context": context is not None}
            )

            return sentiment

        except Exception as e:
            logger.error(f"Sentiment analysis failed for user {user.id}: {e}")
            raise

    async def transcribe_audio(
        self,
        user: User,
        audio_data: bytes,
        format: str = "wav",
        real_time: bool = False
    ) -> dict[str, Any]:
        """Transcribe audio data.
        
        Args:
            user: Authenticated user
            audio_data: Audio data to transcribe
            format: Audio format
            real_time: Whether to use real-time transcription
            
        Returns:
            Transcription results
        """
        if not self._check_permission(user, AIServicePermission.TRANSCRIPTION):
            raise PermissionError("User lacks permission for transcription")

        try:
            transcription = await self.transcription_service.transcribe(
                audio_data, format=format, real_time=real_time
            )

            self._track_usage(
                user.id,
                "transcription",
                "transcribe_audio",
                {"format": format, "real_time": real_time, "audio_size": len(audio_data)}
            )

            return transcription

        except Exception as e:
            logger.error(f"Transcription failed for user {user.id}: {e}")
            raise

    async def generate_speech(
        self,
        user: User,
        text: str,
        voice: str = "default",
        real_time: bool = False
    ) -> bytes:
        """Generate speech from text.
        
        Args:
            user: Authenticated user
            text: Text to convert to speech
            voice: Voice to use
            real_time: Whether to use real-time TTS
            
        Returns:
            Audio data
        """
        if not self._check_permission(user, AIServicePermission.TTS):
            raise PermissionError("User lacks permission for TTS")

        try:
            audio = await self.tts_service.generate_speech(
                text, voice=voice, real_time=real_time
            )

            self._track_usage(
                user.id,
                "tts",
                "generate_speech",
                {"text_length": len(text), "voice": voice, "real_time": real_time}
            )

            return audio

        except Exception as e:
            logger.error(f"TTS failed for user {user.id}: {e}")
            raise

    async def summarize_conversation(
        self,
        user: User,
        conversation_data: dict[str, Any],
        summary_type: str = "brief"
    ) -> dict[str, Any]:
        """Summarize conversation.
        
        Args:
            user: Authenticated user
            conversation_data: Conversation data to summarize
            summary_type: Type of summary (brief, detailed, action_items)
            
        Returns:
            Conversation summary
        """
        if not self._check_permission(user, AIServicePermission.SUMMARIZATION):
            raise PermissionError("User lacks permission for summarization")

        try:
            summary = await self.summarization_service.summarize(
                conversation_data, summary_type=summary_type
            )

            self._track_usage(
                user.id,
                "summarization",
                "summarize_conversation",
                {"summary_type": summary_type, "data_size": len(str(conversation_data))}
            )

            return summary

        except Exception as e:
            logger.error(f"Summarization failed for user {user.id}: {e}")
            raise

    async def get_agent_assistance(
        self,
        user: User,
        current_situation: dict[str, Any],
        assistance_type: str = "suggestions"
    ) -> dict[str, Any]:
        """Get AI-powered agent assistance.
        
        Args:
            user: Authenticated user
            current_situation: Current conversation situation
            assistance_type: Type of assistance needed
            
        Returns:
            Agent assistance recommendations
        """
        if not self._check_permission(user, AIServicePermission.AGENT_ASSISTANCE):
            raise PermissionError("User lacks permission for agent assistance")

        try:
            assistance = await self.agent_assistance.get_assistance(
                current_situation, assistance_type=assistance_type
            )

            self._track_usage(
                user.id,
                "agent_assistance",
                "get_assistance",
                {"assistance_type": assistance_type, "situation_size": len(str(current_situation))}
            )

            return assistance

        except Exception as e:
            logger.error(f"Agent assistance failed for user {user.id}: {e}")
            raise

    async def get_analytics(
        self,
        user: User,
        filters: dict[str, Any] | None = None,
        time_range: dict[str, datetime] | None = None
    ) -> dict[str, Any]:
        """Get AI-powered analytics.
        
        Args:
            user: Authenticated user
            filters: Analytics filters
            time_range: Time range for analytics
            
        Returns:
            Analytics data and insights
        """
        if not self._check_permission(user, AIServicePermission.ANALYTICS):
            raise PermissionError("User lacks permission for analytics")

        try:
            analytics = await self.analytics_service.get_analytics(
                filters=filters, time_range=time_range
            )

            self._track_usage(
                user.id,
                "analytics",
                "get_analytics",
                {"has_filters": filters is not None, "has_time_range": time_range is not None}
            )

            return analytics

        except Exception as e:
            logger.error(f"Analytics failed for user {user.id}: {e}")
            raise

    async def automate_workflow(
        self,
        user: User,
        workflow_data: dict[str, Any],
        workflow_type: str
    ) -> dict[str, Any]:
        """Automate workflow using AI.
        
        Args:
            user: Authenticated user
            workflow_data: Workflow data
            workflow_type: Type of workflow to automate
            
        Returns:
            Workflow automation results
        """
        if not self._check_permission(user, AIServicePermission.WORKFLOW_AUTOMATION):
            raise PermissionError("User lacks permission for workflow automation")

        try:
            result = await self.workflow_automation.automate(
                workflow_data, workflow_type=workflow_type
            )

            self._track_usage(
                user.id,
                "workflow_automation",
                "automate",
                {"workflow_type": workflow_type, "data_size": len(str(workflow_data))}
            )

            return result

        except Exception as e:
            logger.error(f"Workflow automation failed for user {user.id}: {e}")
            raise

    async def check_compliance(
        self,
        user: User,
        interaction_data: dict[str, Any],
        compliance_rules: list[str] | None = None
    ) -> dict[str, Any]:
        """Check compliance using AI.
        
        Args:
            user: Authenticated user
            interaction_data: Interaction data to check
            compliance_rules: Specific compliance rules to check
            
        Returns:
            Compliance check results
        """
        if not self._check_permission(user, AIServicePermission.COMPLIANCE_CHECK):
            raise PermissionError("User lacks permission for compliance checking")

        try:
            compliance = await self.compliance_service.check_compliance(
                interaction_data, compliance_rules=compliance_rules
            )

            self._track_usage(
                user.id,
                "compliance",
                "check_compliance",
                {"rules_count": len(compliance_rules) if compliance_rules else 0}
            )

            return compliance

        except Exception as e:
            logger.error(f"Compliance check failed for user {user.id}: {e}")
            raise

    async def share_context(
        self,
        user: User,
        context_data: dict[str, Any],
        target_users: list[str] | None = None
    ) -> dict[str, Any]:
        """Share context using AI-powered context sharing.
        
        Args:
            user: Authenticated user
            context_data: Context data to share
            target_users: Target users to share with
            
        Returns:
            Context sharing results
        """
        if not self._check_permission(user, AIServicePermission.CONTEXT_SHARING):
            raise PermissionError("User lacks permission for context sharing")

        try:
            result = await self.context_sharing.share_context(
                context_data, target_users=target_users
            )

            self._track_usage(
                user.id,
                "context_sharing",
                "share_context",
                {"target_users_count": len(target_users) if target_users else 0}
            )

            return result

        except Exception as e:
            logger.error(f"Context sharing failed for user {user.id}: {e}")
            raise

    async def optimize_audio(
        self,
        user: User,
        audio_data: bytes,
        optimization_type: str = "quality"
    ) -> bytes:
        """Optimize audio using AI.
        
        Args:
            user: Authenticated user
            audio_data: Audio data to optimize
            optimization_type: Type of optimization
            
        Returns:
            Optimized audio data
        """
        if not self._check_permission(user, AIServicePermission.AUDIO_OPTIMIZATION):
            raise PermissionError("User lacks permission for audio optimization")

        try:
            optimized = await self.audio_optimizer.optimize(
                audio_data, optimization_type=optimization_type
            )

            self._track_usage(
                user.id,
                "audio_optimization",
                "optimize",
                {"optimization_type": optimization_type, "audio_size": len(audio_data)}
            )

            return optimized

        except Exception as e:
            logger.error(f"Audio optimization failed for user {user.id}: {e}")
            raise

    async def get_health_status(
        self,
        user: User,
        provider_type: ProviderType | None = None
    ) -> dict[str, Any]:
        """Get AI provider health status.
        
        Args:
            user: Authenticated user
            provider_type: Specific provider type to check
            
        Returns:
            Health status information
        """
        if not self._check_permission(user, AIServicePermission.HEALTH_MONITORING):
            raise PermissionError("User lacks permission for health monitoring")

        try:
            health = await self.health_monitor.get_health_status(provider_type=provider_type)

            self._track_usage(
                user.id,
                "health_monitoring",
                "get_health_status",
                {"provider_type": provider_type}
            )

            return health

        except Exception as e:
            logger.error(f"Health monitoring failed for user {user.id}: {e}")
            raise

    def get_usage_stats(self, user_id: str) -> dict[str, Any]:
        """Get usage statistics for a user.
        
        Args:
            user_id: User identifier
            
        Returns:
            Usage statistics
        """
        return self.usage_tracker.get(user_id, {
            "total_requests": 0,
            "services": {},
            "first_used": None,
            "last_used": None,
        })

    def get_all_usage_stats(self) -> dict[str, Any]:
        """Get usage statistics for all users.
        
        Returns:
            All usage statistics
        """
        total_requests = sum(
            user_usage["total_requests"]
            for user_usage in self.usage_tracker.values()
        )

        service_stats = {}
        for user_usage in self.usage_tracker.values():
            for service, service_data in user_usage["services"].items():
                if service not in service_stats:
                    service_stats[service] = {"requests": 0, "users": set()}
                service_stats[service]["requests"] += service_data["requests"]
                service_stats[service]["users"].add(user_usage.get("user_id", "unknown"))

        # Convert sets to counts
        for service in service_stats:
            service_stats[service]["users"] = len(service_stats[service]["users"])

        return {
            "total_requests": total_requests,
            "total_users": len(self.usage_tracker),
            "service_stats": service_stats,
            "last_updated": datetime.now(UTC),
        }


# Global instance - lazy initialization
_authenticated_ai_service: AuthenticatedAIService | None = None

def get_authenticated_ai_service() -> AuthenticatedAIService:
    """Get the global authenticated AI service instance."""
    global _authenticated_ai_service
    if _authenticated_ai_service is None:
        _authenticated_ai_service = AuthenticatedAIService()
    return _authenticated_ai_service

# For backward compatibility - create a simple object that proxies to the service
class _ServiceProxy:
    def __getattr__(self, name):
        service = get_authenticated_ai_service()
        return getattr(service, name)

authenticated_ai_service = _ServiceProxy()
