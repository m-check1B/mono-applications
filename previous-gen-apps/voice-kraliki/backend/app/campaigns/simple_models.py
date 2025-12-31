
from pydantic import BaseModel


class ScriptStep(BaseModel):
    text: str
    is_wait: bool = False
    is_transfer: bool = False


class SimpleCampaign(BaseModel):
    id: int
    name: str
    language: str
    category: str
    steps: list[ScriptStep]


class ExecutionSession(BaseModel):
    session_id: str
    campaign_id: int
    current_step: int = 0
    is_active: bool = True
    responses: list[str] = []


class ExecutionRequest(BaseModel):
    campaign_id: int


class ExecutionResponse(BaseModel):
    session_id: str
    current_step: ScriptStep
    step_number: int
    total_steps: int
    is_complete: bool


class ResponseRequest(BaseModel):
    session_id: str
    response: str
