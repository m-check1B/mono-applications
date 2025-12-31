"""
Campaign models for managing call campaign scripts and execution.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator


class CampaignType(str, Enum):
    OUTBOUND = "outbound"
    INBOUND = "inbound"
    INCOMING = "incoming"  # Legacy support


class ValidationType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    BOOLEAN = "boolean"
    EMAIL = "email"
    PHONE = "phone"


class ScriptStepType(str, Enum):
    STATEMENT = "statement"
    QUESTION = "question"
    CONDITIONAL = "conditional"
    GO_TO = "goTo"
    DISPOSITION = "disposition"
    END_CALL = "endCall"
    INITIATE_TRANSFER = "initiateTransfer"


class AgentPersona(BaseModel):
    name: str
    tone: str
    human_emulation: bool = Field(alias="humanEmulation")
    recorded_message_confirmation: str = Field(alias="recordedMessageConfirmation")
    vocabulary_restrictions: list[str] = Field(alias="vocabularyRestrictions")
    behavioral_guidelines: dict[str, Any] = Field(alias="behavioralGuidelines")
    focus_and_handling_policy: dict[str, Any] = Field(alias="focusAndHandlingPolicy")
    disposition_options: list[str] = Field(alias="dispositionOptions")


class DemoCustomerPersona(BaseModel):
    name: str
    age: int
    location: str
    occupation: str
    background: str
    current_situation: dict[str, Any] = Field(alias="currentSituation")
    communication_style: str = Field(alias="communicationStyle")
    pain_points: list[str] = Field(alias="painPoints")
    notes: str


class InvalidResponseHandler(BaseModel):
    condition: str
    response: str


class DisqualificationRule(BaseModel):
    condition: str
    reason: str


class ScriptField(BaseModel):
    field: str
    validation: ValidationType
    notes: str | None = None
    source_field: str | None = Field(alias="sourceField", default=None)
    invalid_response_handlers: list[InvalidResponseHandler] | None = Field(
        alias="invalidResponseHandlers", default=None
    )
    disqualification_rule: DisqualificationRule | None = Field(
        alias="disqualificationRule", default=None
    )


class CustomerData(BaseModel):
    optional_fields_pre_transfer: list[ScriptField] = Field(
        alias="optionalFieldsPreTransfer"
    )


class TransferData(BaseModel):
    transfer_number: str = Field(alias="transferNumber")
    agent_name: str = Field(alias="agentName")
    warm_transfer_introduction_agent: str = Field(
        alias="warmTransferIntroductionAgent"
    )
    warm_transfer_introduction_customer: str = Field(
        alias="warmTransferIntroductionCustomer"
    )
    specialist_not_available_message: str = Field(
        alias="specialistNotAvailableMessage"
    )


class ScriptStep(BaseModel):
    type: ScriptStepType
    content: str | None = None
    content_from_field: str | None = Field(alias="contentFromField", default=None)
    response_variable: str | None = Field(alias="responseVariable", default=None)
    field_details: str | list[str] | None = Field(alias="fieldDetails", default=None)
    gather_fields: list[str] | None = Field(alias="gatherFields", default=None)
    condition: str | None = None
    next_steps: str | list[str] | None = Field(alias="nextSteps", default=None)
    target: str | None = None
    value: str | None = None
    transfer_number: str | None = Field(alias="transferNumber", default=None)
    on_agent_connect: dict[str, Any] | None = Field(alias="onAgentConnect", default=None)
    on_failure: dict[str, Any] | None = Field(alias="onFailure", default=None)


class Script(BaseModel):
    start: list[ScriptStep]
    opening: list[ScriptStep] | None = None
    ask_vehicle_count: list[ScriptStep] | None = Field(alias="askVehicleCount", default=None)
    ask_claims_count: list[ScriptStep] | None = Field(alias="askClaimsCount", default=None)
    ask_vehicle_details: list[ScriptStep] | None = Field(alias="askVehicleDetails", default=None)
    ask_current_insurance: list[ScriptStep] | None = Field(alias="askCurrentInsurance", default=None)
    prepare_transfer: list[ScriptStep] | None = Field(alias="prepareTransfer", default=None)
    transfer: list[ScriptStep] | None = None
    disqualify_invalid_vehicle_count: list[ScriptStep] | None = Field(
        alias="disqualifyInvalidVehicleCount", default=None
    )
    disqualify_too_many_claims: list[ScriptStep] | None = Field(
        alias="disqualifyTooManyClaims", default=None
    )
    end_call_not_qualified: list[ScriptStep] | None = Field(
        alias="endCallNotQualified", default=None
    )
    end_call_no_recording: list[ScriptStep] | None = Field(
        alias="endCallNoRecording", default=None
    )
    end_call_wrong_person: list[ScriptStep] | None = Field(
        alias="endCallWrongPerson", default=None
    )
    end_call_not_authorized: list[ScriptStep] | None = Field(
        alias="endCallNotAuthorized", default=None
    )
    end_call_callback: list[ScriptStep] | None = Field(alias="endCallCallback", default=None)
    end_call_data_failed: list[ScriptStep] | None = Field(
        alias="endCallDataFailed", default=None
    )
    end_call_specialist_unavailable: list[ScriptStep] | None = Field(
        alias="endCallSpecialistUnavailable", default=None
    )
    end_call: list[ScriptStep] | None = None

    class Config:
        extra = "allow"  # Allow additional script sections


class CallContext(BaseModel):
    """Alternative to demo customer persona for some campaigns."""
    organization: str | None = None
    calling_on_behalf_of: bool | None = Field(alias="callingOnBehalfOf", default=None)
    purpose: str | None = None
    pac_details: dict[str, Any] | None = Field(alias="pacDetails", default=None)
    caller_id_source_info: str | None = Field(alias="callerIdSourceInfo", default=None)
    donation_tiers: dict[str, Any] | None = Field(alias="donationTiers", default=None)
    donation_strategy: str | None = Field(alias="donationStrategy", default=None)
    data_points: list[dict[str, Any]] | None = Field(alias="dataPoints", default=None)

    class Config:
        extra = "allow"


class TransferDataAlternative(BaseModel):
    """Alternative transfer data structure for some campaigns."""
    transfer_department: str | None = Field(alias="transferDepartment", default=None)
    escalation_scenarios: dict[str, Any] | None = Field(alias="escalationScenarios", default=None)

    class Config:
        extra = "allow"


class Campaign(BaseModel):
    id: int
    type: CampaignType
    language: str
    category: str
    title: str
    campaign: str
    agent_persona: AgentPersona = Field(alias="agentPersona")
    demo_customer_persona: DemoCustomerPersona | None = Field(alias="demoCustomerPersona", default=None)
    call_context: CallContext | None = Field(alias="callContext", default=None)
    customer_data: CustomerData | None = Field(alias="customerData", default=None)
    transfer_data: TransferData | None = Field(alias="transferData", default=None)
    transfer_data_alt: TransferDataAlternative | None = Field(alias="transferDepartment", default=None)
    script: Script

    # Handle legacy incoming type
    @validator('type', pre=True)
    def normalize_type(cls, v):
        if v == 'incoming':
            return CampaignType.INCOMING
        return v

    class Config:
        extra = "allow"  # Allow additional fields
