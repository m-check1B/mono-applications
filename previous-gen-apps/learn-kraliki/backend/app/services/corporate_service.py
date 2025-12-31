"""
Corporate Service
Business logic for corporate team operations
"""

from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import uuid

from app.models.corporate import CorporateTeam, TeamMember


def utcnow():
    return datetime.now(timezone.utc)


class CorporateService:
    """Service for corporate team management."""

    def create_team(self, team_data: dict, db: Session) -> CorporateTeam:
        """Create a new corporate team."""
        team_id = str(uuid.uuid4())

        team = CorporateTeam(
            id=team_id,
            company_name=team_data["company_name"],
            contact_email=team_data["contact_email"],
            contact_name=team_data["contact_name"],
            package_type=team_data["package_type"],
            seat_count=team_data["seat_count"],
            price_eur=team_data["price_eur"],
            billing_period=team_data.get("billing_period", "one_time"),
            custom_branding=team_data.get("custom_branding", False),
            company_logo_url=team_data.get("company_logo_url"),
            status="active",
        )

        db.add(team)
        db.commit()
        db.refresh(team)

        return team

    def get_team(self, team_id: str, db: Session) -> Optional[CorporateTeam]:
        """Get a team by ID."""
        return db.query(CorporateTeam).filter(CorporateTeam.id == team_id).first()

    def get_team_progress(self, team_id: str, db: Session) -> Optional[dict]:
        """Get team progress overview."""
        team = self.get_team(team_id, db)
        if not team:
            return None

        members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()

        total_members = len(members)
        active_members = sum(1 for m in members if m.status == "active")
        completed_members = sum(1 for m in members if m.status == "completed")
        certificates_issued = sum(1 for m in members if m.certificate_issued)

        # Calculate average progress (simplified: based on completion status)
        average_progress = (
            (completed_members / total_members * 100) if total_members > 0 else 0
        )

        return {
            "team_id": team_id,
            "company_name": team.company_name,
            "total_members": total_members,
            "active_members": active_members,
            "completed_members": completed_members,
            "certificates_issued": certificates_issued,
            "average_progress": round(average_progress, 2),
        }

    def generate_team_report(self, team_id: str, db: Session) -> Optional[dict]:
        """Generate manager report for a team."""
        team = self.get_team(team_id, db)
        if not team:
            return None

        members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()

        completed_members = [m for m in members if m.status == "completed"]
        certification_rate = (
            (len(completed_members) / len(members) * 100) if members else 0
        )

        member_details = []
        for member in members:
            member_details.append(
                {
                    "id": member.id,
                    "user_email": member.user_email,
                    "user_name": member.user_name,
                    "status": member.status,
                    "certificate_issued": member.certificate_issued,
                    "enrolled_at": member.enrolled_at.isoformat()
                    if member.enrolled_at
                    else None,
                    "completed_at": member.completed_at.isoformat()
                    if member.completed_at
                    else None,
                    "last_activity": member.last_activity.isoformat()
                    if member.last_activity
                    else None,
                }
            )

        # Course breakdown (simplified for now)
        course_breakdown = [
            {
                "course_slug": "ai-fundamentals-cs",
                "course_name": "AI Academy Level 1 (Česky)",
                "enrolled": len(members),
                "completed": len(completed_members),
                "completion_rate": round(certification_rate, 2),
            }
        ]

        return {
            "team_id": team_id,
            "company_name": team.company_name,
            "report_generated_at": utcnow().isoformat(),
            "total_seats": team.seat_count,
            "active_enrollments": len(
                [m for m in members if m.status in ["enrolled", "active"]]
            ),
            "completed_courses": len(completed_members),
            "certification_rate": round(certification_rate, 2),
            "members": member_details,
            "course_breakdown": course_breakdown,
        }

    def add_team_member(
        self, team_id: str, member_data: dict, db: Session
    ) -> Optional[TeamMember]:
        """Add a member to a corporate team."""
        team = self.get_team(team_id, db)
        if not team:
            return None

        # Check if seats are available
        current_members = (
            db.query(TeamMember).filter(TeamMember.team_id == team_id).count()
        )
        if current_members >= team.seat_count:
            return None

        member_id = str(uuid.uuid4())

        member = TeamMember(
            id=member_id,
            team_id=team_id,
            user_id=member_data["user_id"],
            user_email=member_data["user_email"],
            user_name=member_data.get("user_name"),
            status="invited",
        )

        db.add(member)
        db.commit()
        db.refresh(member)

        return member

    def list_team_members(
        self, team_id: str, db: Session
    ) -> Optional[List[TeamMember]]:
        """List all members of a corporate team."""
        team = self.get_team(team_id, db)
        if not team:
            return None

        return db.query(TeamMember).filter(TeamMember.team_id == team_id).all()

    def remove_team_member(self, team_id: str, member_id: str, db: Session) -> bool:
        """Remove a member from a corporate team."""
        team = self.get_team(team_id, db)
        if not team:
            return False

        member = (
            db.query(TeamMember)
            .filter(TeamMember.id == member_id, TeamMember.team_id == team_id)
            .first()
        )

        if not member:
            return False

        db.delete(member)
        db.commit()

        return True

    def issue_certificate(self, member_id: str, db: Session) -> Optional[dict]:
        """Issue certificate to a team member."""
        member = db.query(TeamMember).filter(TeamMember.id == member_id).first()
        if not member:
            return None

        # Check if eligible (completed course)
        if member.status != "completed":
            return None

        # Generate certificate URL (simplified - in production, generate actual PDF)
        certificate_url = f"/certificates/{member_id}.pdf"

        member.certificate_issued = True
        member.certificate_url = certificate_url
        member.certificate_issued_at = utcnow()

        db.commit()

        return {
            "member_id": member_id,
            "certificate_url": certificate_url,
            "issued_at": member.certificate_issued_at.isoformat(),
        }

    def get_certificate(self, member_id: str, db: Session) -> Optional[dict]:
        """Get certificate for a team member."""
        member = db.query(TeamMember).filter(TeamMember.id == member_id).first()

        if not member or not member.certificate_issued:
            return None

        return {
            "member_id": member_id,
            "certificate_url": member.certificate_url,
            "issued_at": member.certificate_issued_at.isoformat()
            if member.certificate_issued_at
            else None,
            "user_name": member.user_name,
            "user_email": member.user_email,
            "team_id": member.team_id,
        }


# Singleton instance
corporate_service = CorporateService()
