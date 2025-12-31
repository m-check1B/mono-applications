import json
import logging
import os
from typing import Dict, Any, List, Optional
from openai import OpenAI
from app.services.n8n_client import get_n8n_client

logger = logging.getLogger(__name__)

class SwarmOrchestrator:
    """
    Orchestrates complex multi-agent sequences (Darwin2).
    In Phase 3, this primarily routes to high-reasoning models or specialized n8n flows.
    """
    
    def __init__(self, db_session=None):
        self.db = db_session
        self.n8n = get_n8n_client()
        self._client = None

    def get_client(self):
        if self._client is None:
            self._client = OpenAI(
                api_key=os.environ.get("AI_INTEGRATIONS_OPENROUTER_API_KEY"),
                base_url=os.environ.get("AI_INTEGRATIONS_OPENROUTER_BASE_URL")
            )
        return self._client

    async def execute_swarm(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executes a swarm sequence based on user input.
        """
        logger.info(f"[Swarm] Initiating swarm for: {message[:50]}...")
        
        try:
            # 1. Intent Decompostion via Director Agent
            prompt = f"""You are the Darwin2 Swarm Director. Decompose the following user request into a sequence of specialist agent actions.

User Request: {message}

Return a JSON object with:
1. "summary": A brief summary of the plan.
2. "steps": A list of steps, each with "agent" (e.g., Researcher, Executor, Critic) and "action".
3. "final_response": A proactive response to the user explaining what the swarm will do.

JSON Format:
{{
  "summary": "...",
  "steps": [{{ "agent": "...", "action": "..." }}],
  "final_response": "..."
}}"""

            response = self.get_client().chat.completions.create(
                model="openai/gpt-4o-mini", # Use a fast model for orchestration planning
                messages=[{"role": "user", "content": prompt}],
                response_format={ "type": "json_object" }
            )
            
            swarm_result = json.loads(response.choices[0].message.content)
            return swarm_result

        except Exception as e:
            logger.error(f"[Swarm] Planning failed: {str(e)}")
            return {
                "summary": "Swarm fallback activated.",
                "steps": [{"agent": "Director", "action": "Standard execution mode."}],
                "final_response": f"The Darwin2 Swarm is processing your request: '{message}'. Plan finalized."
            }

def get_swarm_orchestrator(db=None):
    return SwarmOrchestrator(db)
