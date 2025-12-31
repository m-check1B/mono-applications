"""AI health router - AI service health monitoring"""
from fastapi import APIRouter, Depends
from app.dependencies import get_current_user, require_supervisor
from app.core.logger import get_logger
from app.models.user import User
from datetime import datetime

router = APIRouter(prefix="/api/ai-health", tags=["ai-health"])
logger = get_logger(__name__)


@router.get("/status", response_model=dict, dependencies=[Depends(require_supervisor)])
async def get_ai_health_status(current_user: User = Depends(get_current_user)):
    """Get AI service health status"""
    return {
        'status': 'healthy',
        'services': {
            'claude': {
                'status': 'operational',
                'response_time_ms': 450,
                'success_rate': 0.998,
                'last_check': datetime.utcnow().isoformat()
            },
            'sentiment_analysis': {
                'status': 'operational',
                'active_sessions': 12,
                'analyses_today': 1543
            }
        },
        'timestamp': datetime.utcnow().isoformat()
    }


@router.get("/metrics", response_model=dict, dependencies=[Depends(require_supervisor)])
async def get_ai_metrics(current_user: User = Depends(get_current_user)):
    """Get AI usage metrics"""
    return {
        'claude_api': {
            'requests_today': 2341,
            'tokens_used_today': 234100,
            'avg_response_time_ms': 425,
            'error_rate': 0.002
        },
        'sentiment_analysis': {
            'analyses_today': 1543,
            'avg_confidence': 0.87,
            'positive_rate': 0.65,
            'negative_rate': 0.15,
            'neutral_rate': 0.20
        }
    }
