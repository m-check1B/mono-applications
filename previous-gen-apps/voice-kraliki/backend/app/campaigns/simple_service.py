import logging
import re
import uuid
from pathlib import Path

from .simple_models import ExecutionResponse, ExecutionSession, ScriptStep, SimpleCampaign

logger = logging.getLogger(__name__)


class SimpleCampaignService:
    def __init__(self):
        self.campaigns: dict[int, SimpleCampaign] = {}
        self.sessions: dict[str, ExecutionSession] = {}
        self.scripts_dir = Path(__file__).parent / "scripts"
        self._load_campaigns()

    def _load_campaigns(self):
        """Load all campaigns from markdown files"""
        if not self.scripts_dir.exists():
            return

        for file_path in self.scripts_dir.glob("*.md"):
            campaign = self._parse_markdown_file(file_path)
            if campaign:
                self.campaigns[campaign.id] = campaign

    def _parse_markdown_file(self, file_path: Path) -> SimpleCampaign | None:
        """Parse a markdown file with YAML frontmatter"""
        try:
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Extract YAML frontmatter
            frontmatter_match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
            if not frontmatter_match:
                return None

            frontmatter_text = frontmatter_match.group(1)
            script_content = frontmatter_match.group(2).strip()

            # Parse YAML frontmatter
            metadata = {}
            for line in frontmatter_text.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()

            # Parse script steps
            steps = []
            lines = script_content.split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Check for wait instructions
                if line.startswith('*[') and line.endswith(']*'):
                    steps.append(ScriptStep(text=line, is_wait=True))
                # Check for transfer instruction
                elif line.startswith('*[TRANSFER]*'):
                    steps.append(ScriptStep(text=line, is_transfer=True))
                # Regular dialogue
                else:
                    steps.append(ScriptStep(text=line))

            return SimpleCampaign(
                id=int(metadata.get('id', 0)),
                name=metadata.get('name', 'Unknown Campaign'),
                language=metadata.get('language', 'en'),
                category=metadata.get('category', 'general'),
                steps=steps
            )

        except Exception as e:
            logger.error("Error parsing file %s: %s", file_path, e)
            return None

    def get_all_campaigns(self) -> list[SimpleCampaign]:
        """Get all available campaigns"""
        return list(self.campaigns.values())

    def get_campaign_by_id(self, campaign_id: int) -> SimpleCampaign | None:
        """Get a specific campaign by ID"""
        return self.campaigns.get(campaign_id)

    def start_execution(self, campaign_id: int) -> ExecutionResponse | None:
        """Start executing a campaign"""
        campaign = self.get_campaign_by_id(campaign_id)
        if not campaign or not campaign.steps:
            return None

        session_id = str(uuid.uuid4())
        session = ExecutionSession(
            session_id=session_id,
            campaign_id=campaign_id,
            current_step=0,
            is_active=True
        )

        self.sessions[session_id] = session

        return ExecutionResponse(
            session_id=session_id,
            current_step=campaign.steps[0],
            step_number=1,
            total_steps=len(campaign.steps),
            is_complete=False
        )

    def process_response(self, session_id: str, response: str) -> ExecutionResponse | None:
        """Process a response and move to next step"""
        session = self.sessions.get(session_id)
        if not session or not session.is_active:
            return None

        campaign = self.get_campaign_by_id(session.campaign_id)
        if not campaign:
            return None

        # Add response to session
        session.responses.append(response)

        # Move to next step
        session.current_step += 1

        # Check if campaign is complete
        if session.current_step >= len(campaign.steps):
            session.is_active = False
            return ExecutionResponse(
                session_id=session_id,
                current_step=ScriptStep(text="Campaign completed"),
                step_number=len(campaign.steps),
                total_steps=len(campaign.steps),
                is_complete=True
            )

        current_step = campaign.steps[session.current_step]

        # If it's a wait step, automatically move to next step
        if current_step.is_wait:
            return self.process_response(session_id, "[WAIT PROCESSED]")

        # If it's a transfer step, end the campaign
        if current_step.is_transfer:
            session.is_active = False
            return ExecutionResponse(
                session_id=session_id,
                current_step=current_step,
                step_number=session.current_step + 1,
                total_steps=len(campaign.steps),
                is_complete=True
            )

        return ExecutionResponse(
            session_id=session_id,
            current_step=current_step,
            step_number=session.current_step + 1,
            total_steps=len(campaign.steps),
            is_complete=False
        )

    def get_session(self, session_id: str) -> ExecutionSession | None:
        """Get session details"""
        return self.sessions.get(session_id)

    def stop_session(self, session_id: str) -> bool:
        """Stop an active session"""
        if session_id in self.sessions:
            self.sessions[session_id].is_active = False
            return True
        return False
