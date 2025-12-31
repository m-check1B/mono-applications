"""
Corporate Router
Endpoints for corporate team management and B2B training packages
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.corporate import CorporateTeam, TeamMember
from app.schemas.corporate import (
    CorporateTeamCreate,
    CorporateTeamResponse,
    TeamMemberCreate,
    TeamMemberResponse,
    TeamProgressResponse,
    TeamReportResponse,
)
from app.services.corporate_service import corporate_service

router = APIRouter(prefix="/corporate", tags=["corporate"])


@router.post("/teams", response_model=CorporateTeamResponse)
async def create_team(team_data: CorporateTeamCreate, db: Session = get_db()):
    """Create a new corporate team."""
    team = corporate_service.create_team(team_data, db)
    return team


@router.get("/teams/{team_id}", response_model=CorporateTeamResponse)
async def get_team(team_id: str, db: Session = get_db()):
    """Get team details."""
    team = corporate_service.get_team(team_id, db)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.get("/teams/{team_id}/progress", response_model=TeamProgressResponse)
async def get_team_progress(team_id: str, db: Session = get_db()):
    """Get team progress overview."""
    progress = corporate_service.get_team_progress(team_id, db)
    if not progress:
        raise HTTPException(status_code=404, detail="Team not found")
    return progress


@router.get("/reports/{team_id}", response_model=TeamReportResponse)
async def generate_team_report(team_id: str, db: Session = get_db()):
    """Generate manager report for team."""
    report = corporate_service.generate_team_report(team_id, db)
    if not report:
        raise HTTPException(status_code=404, detail="Team not found")
    return report


@router.post("/teams/{team_id}/members", response_model=TeamMemberResponse)
async def add_team_member(
    team_id: str, member_data: TeamMemberCreate, db: Session = get_db()
):
    """Add a member to a corporate team."""
    member = corporate_service.add_team_member(team_id, member_data, db)
    if not member:
        raise HTTPException(status_code=404, detail="Team not found or seats full")
    return member


@router.get("/teams/{team_id}/members", response_model=List[TeamMemberResponse])
async def list_team_members(team_id: str, db: Session = get_db()):
    """List all members of a corporate team."""
    members = corporate_service.list_team_members(team_id, db)
    if members is None:
        raise HTTPException(status_code=404, detail="Team not found")
    return members


@router.delete("/teams/{team_id}/members/{member_id}")
async def remove_team_member(team_id: str, member_id: str, db: Session = get_db()):
    """Remove a member from a corporate team."""
    success = corporate_service.remove_team_member(team_id, member_id, db)
    if not success:
        raise HTTPException(status_code=404, detail="Team or member not found")
    return {"status": "success"}


@router.post("/certificates/{member_id}")
async def issue_certificate(member_id: str, db: Session = get_db()):
    """Issue certificate to a team member."""
    certificate = corporate_service.issue_certificate(member_id, db)
    if not certificate:
        raise HTTPException(status_code=404, detail="Member not found or not eligible")
    return certificate


@router.get("/certificates/{member_id}")
async def get_certificate(member_id: str, db: Session = get_db()):
    """Get certificate for a team member."""
    certificate = corporate_service.get_certificate(member_id, db)
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return certificate
