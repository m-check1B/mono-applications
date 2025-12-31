import sys
import os
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.task import Task, Project, TaskStatus
from app.models.shadow_profile import ShadowProfile
from app.services.sales_service import SalesService
from app.services.shadow_analyzer import ShadowAnalyzerService
import asyncio
import uuid

async def test_automation():
    db = SessionLocal()
    try:
        # 1. Create a dummy user
        user_id = str(uuid.uuid4())
        user = User(
            id=user_id,
            email=f"test_{user_id[:8]}@example.com",
            username=f"testuser_{user_id[:8]}",
            passwordHash="hashed_password"
        )
        db.add(user)
        
        # 2. Create a project
        project_id = str(uuid.uuid4())
        project = Project(
            id=project_id,
            name="Mega Corp AI Audit",
            userId=user_id
        )
        db.add(project)
        
        # 3. Create tasks with audit data
        tasks = [
            Task(
                id=str(uuid.uuid4()),
                title="Manual Invoice Entry",
                description="Staff manually typing invoices into ERP.",
                projectId=project_id,
                userId=user_id,
                aiInsights={"human_cost": 25000, "ai_cost": 250},
                tags=["quick-win"]
            ),
            Task(
                id=str(uuid.uuid4()),
                title="Customer Support Triage",
                description="Sorting 500 emails daily by hand.",
                projectId=project_id,
                userId=user_id,
                aiInsights={"human_cost": 45000, "ai_cost": 1500},
                tags=["high-impact"]
            ),
            Task(
                id=str(uuid.uuid4()),
                title="Monthly Reporting",
                description="Aggregating Excel sheets for 3 days.",
                projectId=project_id,
                userId=user_id,
                aiInsights={"human_cost": 12000, "ai_cost": 120},
                tags=["quick-win"]
            )
        ]
        for t in tasks:
            db.add(t)
            
        # 4. Create Shadow Profile
        shadow_service = ShadowAnalyzerService(db)
        await shadow_service.create_profile(user_id)
        
        db.commit()
        
        print(f"Created data for user {user_id} and project {project_id}")
        
        # 5. Generate Report
        report_content = await SalesService.generate_automated_audit(db, user_id, project_id)
        
        print("\n--- GENERATED REPORT ---")
        print(report_content)
        print("--- END OF REPORT ---\n")
        
        # Verify placeholders were replaced
        assert "Mega Corp AI Audit" in report_content
        assert "Manual Invoice Entry" in report_content
        assert "€80,130.0" in report_content
        assert "Shadow Analysis" in report_content
        
        print("Validation Successful!")
        
    finally:
        # Cleanup
        # db.query(Task).filter(Task.userId == user_id).delete()
        # db.query(Project).filter(Project.userId == user_id).delete()
        # db.query(ShadowProfile).filter(ShadowProfile.user_id == user_id).delete()
        # db.query(User).filter(User.id == user_id).delete()
        # db.commit()
        db.close()

if __name__ == "__main__":
    asyncio.run(test_automation())
