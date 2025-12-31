import logging
import httpx
import json
from typing import Any, Dict, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)

class N8nClient:
    """
    Client for interacting with n8n workflow automation platform.
    Supports multi-tenancy by allowing per-workspace overrides for n8n connection.
    """

    def __init__(self, workspace_settings: Optional[Dict[str, Any]] = None):
        """
        Initialize the n8n client.
        
        Args:
            workspace_settings: Optional workspace-level settings dict which may contain:
                - n8n_url: User's custom n8n URL
                - n8n_api_key: User's custom n8n API key
        """
        # Default to global settings
        self.base_url = settings.N8N_URL
        self.api_key = settings.N8N_API_KEY

        # Apply workspace overrides if present
        if workspace_settings:
            self.base_url = workspace_settings.get("n8n_url", self.base_url)
            self.api_key = workspace_settings.get("n8n_api_key", self.api_key)

        if not self.base_url:
            logger.warning("N8N_URL is not configured globally or in workspace settings.")

    async def trigger_webhook(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger an n8n webhook.
        
        Args:
            path: The webhook path (e.g., 'invoice-paid' or 'handleRequest')
            payload: The JSON payload to send
            
        Returns:
            The response from n8n
        """
        if not self.base_url:
            raise ValueError("n8n base URL is not configured.")

        # Ensure path starts correctly
        if not path.startswith("/") and not self.base_url.endswith("/"):
            url = f"{self.base_url}/{path}"
        else:
            url = f"{self.base_url}{path}"

        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["X-N8N-API-KEY"] = self.api_key

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json() if response.content else {"status": "success"}
            except httpx.HTTPStatusError as e:
                logger.error(f"n8n webhook failed with status {e.response.status_code}: {e.response.text}")
                raise
            except Exception as e:
                logger.error(f"Error triggering n8n webhook: {str(e)}")
                raise

    async def dispatch_event(self, event: Dict[str, Any], path: str = "events") -> Dict[str, Any]:
        """
        Standardized method to dispatch events to n8n following the platform event schema.
        
        Args:
            event: The event envelope (matches app.core.events.EventPublisher.publish format)
            path: Default webhook path for generic events
        """
        return await self.trigger_webhook(path, event)

    async def orchestrate_flow(self, flow_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Trigger a specific orchestration flow in n8n.
        
        Args:
            flow_id: Identifier of the workflow (e.g., 'research-prospect', 'generate-content')
            context: Dictionary of data required for the flow
        """
        payload = {
            "flow_id": flow_id,
            "context": context,
            "source": "focus-kraliki-backend"
        }
        return await self.trigger_webhook(f"orchestrate/{flow_id}", payload)

def get_n8n_client(workspace_settings: Optional[Dict[str, Any]] = None) -> N8nClient:
    """Helper to get an n8n client with current configuration."""
    return N8nClient(workspace_settings)
