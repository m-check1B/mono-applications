"""Circuit breaker router - Resilience and failure handling"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime, timedelta
from app.dependencies import get_current_user, require_supervisor
from app.core.logger import get_logger
from app.models.user import User

router = APIRouter(prefix="/api/circuit-breaker", tags=["circuit-breaker"])
logger = get_logger(__name__)

# In-memory circuit breaker state (would use Redis in production)
circuit_states: Dict[str, dict] = {}


class CircuitBreakerConfig(BaseModel):
    """Circuit breaker configuration"""
    service_name: str
    failure_threshold: int = 5
    timeout_seconds: int = 60
    half_open_requests: int = 3


@router.get("/status", response_model=dict, dependencies=[Depends(require_supervisor)])
async def get_circuit_breaker_status(current_user: User = Depends(get_current_user)):
    """
    Get status of all circuit breakers

    **Protected**: Requires supervisor role
    """
    services = ['twilio', 'ai', 'database', 'redis']

    status_list = []
    for service in services:
        state = circuit_states.get(service, {
            'state': 'closed',
            'failure_count': 0,
            'last_failure': None,
            'last_success': datetime.utcnow().isoformat()
        })
        status_list.append({
            'service': service,
            **state
        })

    return {
        'circuit_breakers': status_list,
        'timestamp': datetime.utcnow().isoformat()
    }


@router.post("/configure", response_model=dict, dependencies=[Depends(require_supervisor)])
async def configure_circuit_breaker(
    config: CircuitBreakerConfig,
    current_user: User = Depends(get_current_user)
):
    """
    Configure circuit breaker for a service

    **Protected**: Requires supervisor role
    """
    circuit_states[config.service_name] = {
        'state': 'closed',
        'failure_count': 0,
        'failure_threshold': config.failure_threshold,
        'timeout_seconds': config.timeout_seconds,
        'half_open_requests': config.half_open_requests,
        'last_failure': None,
        'last_success': datetime.utcnow().isoformat()
    }

    return {
        'success': True,
        'message': f'Circuit breaker configured for {config.service_name}',
        'config': config.dict()
    }


@router.post("/reset/{service_name}", response_model=dict, dependencies=[Depends(require_supervisor)])
async def reset_circuit_breaker(
    service_name: str,
    current_user: User = Depends(get_current_user)
):
    """
    Reset circuit breaker to closed state

    **Protected**: Requires supervisor role
    """
    if service_name in circuit_states:
        circuit_states[service_name]['state'] = 'closed'
        circuit_states[service_name]['failure_count'] = 0
        circuit_states[service_name]['last_success'] = datetime.utcnow().isoformat()

    return {
        'success': True,
        'message': f'Circuit breaker reset for {service_name}',
        'service': service_name
    }


@router.get("/metrics", response_model=dict, dependencies=[Depends(require_supervisor)])
async def get_circuit_breaker_metrics(current_user: User = Depends(get_current_user)):
    """
    Get circuit breaker metrics

    **Protected**: Requires supervisor role
    """
    total_services = len(circuit_states)
    open_circuits = sum(1 for s in circuit_states.values() if s.get('state') == 'open')
    half_open_circuits = sum(1 for s in circuit_states.values() if s.get('state') == 'half_open')

    return {
        'summary': {
            'total_services': total_services,
            'open_circuits': open_circuits,
            'half_open_circuits': half_open_circuits,
            'closed_circuits': total_services - open_circuits - half_open_circuits
        },
        'services': circuit_states,
        'timestamp': datetime.utcnow().isoformat()
    }
