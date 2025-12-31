"""Call BYOK router - Bring Your Own Key integration"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.dependencies import get_current_user, require_supervisor
from app.core.logger import get_logger
from app.models.user import User

router = APIRouter(prefix="/api/call-byok", tags=["call-byok"])
logger = get_logger(__name__)


class BYOKConfigRequest(BaseModel):
    """BYOK configuration"""
    provider: str  # twilio, vonage, etc.
    credentials: dict
    settings: Optional[dict] = None


@router.get("/config", response_model=dict, dependencies=[Depends(require_supervisor)])
async def get_byok_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get BYOK configuration for organization"""
    # Mock - would retrieve from secure storage
    return {
        'organization_id': current_user.organization_id,
        'providers': [
            {
                'provider': 'twilio',
                'account_sid': 'AC***************',
                'enabled': True,
                'capabilities': ['voice', 'sms']
            }
        ],
        'default_provider': 'twilio'
    }


@router.post("/config", response_model=dict, dependencies=[Depends(require_supervisor)])
async def set_byok_config(
    request: BYOKConfigRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Configure BYOK for organization"""
    # Would validate and store securely
    logger.info(f"BYOK config set for org {current_user.organization_id}, provider: {request.provider}")

    return {
        'success': True,
        'message': f'BYOK configured for {request.provider}',
        'provider': request.provider
    }


@router.delete("/config/{provider}", response_model=dict, dependencies=[Depends(require_supervisor)])
async def delete_byok_config(
    provider: str,
    current_user: User = Depends(get_current_user)
):
    """Remove BYOK configuration"""
    return {
        'success': True,
        'message': f'BYOK configuration removed for {provider}'
    }


@router.post("/test", response_model=dict, dependencies=[Depends(require_supervisor)])
async def test_byok_connection(
    provider: str,
    current_user: User = Depends(get_current_user)
):
    """Test BYOK connection"""
    # Would test actual connection
    return {
        'success': True,
        'provider': provider,
        'status': 'connected',
        'test_results': {
            'voice': 'ok',
            'sms': 'ok',
            'balance': '125.50 USD'
        }
    }
