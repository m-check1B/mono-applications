"""
Corporate Schemas
Pydantic models for corporate team operations
"""

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class CorporateTeamCreate(BaseModel):
    """Schema for creating a new corporate team."""

    company_name: str
    contact_email: EmailStr
    contact_name: str
    package_type: str  # "team", "corporate", "enterprise"
    seat_count: int
    price_eur: float
    billing_period: str = "one_time"
    custom_branding: bool = False
    company_logo_url: Optional[str] = None


class CorporateTeamResponse(BaseModel):
    """Schema for corporate team response."""

    id: str
    company_name: str
    contact_email: str
    contact_name: str
    package_type: str
    seat_count: int
    price_eur: float
    currency: str
    billing_period: str
    paid_at: Optional[datetime] = None
    payment_id: Optional[str] = None
    invoice_id: Optional[str] = None
    custom_branding: bool
    company_logo_url: Optional[str] = None
    custom_domain: Optional[str] = None
    status: str
    expires_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TeamMemberCreate(BaseModel):
    """Schema for adding a member to a team."""

    user_id: str
    user_email: EmailStr
    user_name: Optional[str] = None


class TeamMemberResponse(BaseModel):
    """Schema for team member response."""

    id: str
    team_id: str
    user_id: str
    user_email: str
    user_name: Optional[str] = None
    status: str
    enrolled_courses: List[dict]
    certificate_issued: bool
    certificate_url: Optional[str] = None
    certificate_issued_at: Optional[datetime] = None
    invited_at: datetime
    enrolled_at: Optional[datetime] = None
    last_activity: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TeamProgressResponse(BaseModel):
    """Schema for team progress overview."""

    team_id: str
    company_name: str
    total_members: int
    active_members: int
    completed_members: int
    certificates_issued: int
    average_progress: float  # Percentage


class TeamReportResponse(BaseModel):
    """Schema for manager report."""

    team_id: str
    company_name: str
    report_generated_at: datetime

    # Summary metrics
    total_seats: int
    active_enrollments: int
    completed_courses: int
    certification_rate: float  # Percentage

    # Member details
    members: List[dict]

    # Progress by course
    course_breakdown: List[dict]
