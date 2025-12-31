import os
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.task import Task, Project
from app.models.shadow_profile import ShadowProfile
from app.services.shadow_analyzer import ShadowAnalyzerService, ARCHETYPES

class SalesService:
    """
    Service for automating Audit-to-Retainer workflow.
    Ingests templates from brain-2026/sales/ and generates personalized reports.
    """
    
    TEMPLATES_DIR = Path("/home/adminmatej/github/brain-2026/sales")
    
    @classmethod
    def get_template(cls, template_name: str) -> str:
        """Read a template file from the sales directory."""
        if not template_name.endswith(".md"):
            template_path = cls.TEMPLATES_DIR / f"{template_name}.md"
        else:
            template_path = cls.TEMPLATES_DIR / template_name
            
        if not template_path.exists():
            raise FileNotFoundError(f"Template {template_name} not found at {template_path}")
        
        with open(template_path, "r") as f:
            return f.read()

    @classmethod
    def list_templates(cls) -> List[str]:
        """List available sales templates."""
        if not cls.TEMPLATES_DIR.exists():
            return []
        return [f.stem for f in cls.TEMPLATES_DIR.glob("*.md")]

    @classmethod
    def generate_report(cls, template_name: str, data: Dict[str, Any]) -> str:
        """
        Generate a report by replacing placeholders in a template.
        Placeholders are in format [Placeholder Name].
        """
        template_content = cls.get_template(template_name)
        
        # Default variables
        if "Date" not in data:
            data["Date"] = datetime.now().strftime("%Y-%m-%d")
            
        report_content = template_content
        
        # Replace simple placeholders
        for key, value in data.items():
            placeholder = f"[{key}]"
            report_content = report_content.replace(placeholder, str(value))
            
        return report_content

    @classmethod
    async def generate_automated_audit(cls, db: Session, user_id: str, project_id: str) -> str:
        """
        Automate the generation of an AUDIT-REPORT-TEMPLATE.md.
        Gathers data from tasks in the project and shadow analysis.
        """
        project = db.query(Project).filter(Project.id == project_id, Project.userId == user_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found for user {user_id}")

        tasks = db.query(Task).filter(Task.projectId == project_id).all()
        
        # Get Shadow Analysis context
        shadow_service = ShadowAnalyzerService(db)
        shadow_profile = await shadow_service.get_profile(user_id)
        
        # Prepare data for template
        data = {
            "Client Name": project.name,
            "Date": datetime.now().strftime("%Y-%m-%d"),
        }
        
        # Calculate Manual Tax Breakdown (Processes)
        # We look for tasks that have audit-specific data in aiInsights
        processes_table = ""
        total_savings = 0
        process_count = 0
        
        for task in tasks:
            insights = task.aiInsights or {}
            if "human_cost" in insights and "ai_cost" in insights:
                process_count += 1
                human_cost = float(insights.get("human_cost", 0))
                ai_cost = float(insights.get("ai_cost", 0))
                ratio = round(human_cost / ai_cost, 1) if ai_cost > 0 else 100
                savings = human_cost - ai_cost
                total_savings += savings
                
                processes_table += f"| {task.title} | €{human_cost:,} | €{ai_cost:,} | {ratio}x |\n"
                
                # Map to Process 1, Process 2 etc for simple replacement
                data[f"Process {process_count}"] = task.title
                data[f"Cost {process_count}"] = f"{human_cost:,}"
                data[f"AI Cost {process_count}"] = f"{ai_cost:,}"
                data[f"Ratio {process_count}"] = f"{ratio}"

        data["Amount"] = f"{total_savings:,}"
        
        # Quick Wins
        quick_wins = [t for t in tasks if t.tags and "quick-win" in t.tags]
        for i, qw in enumerate(quick_wins[:3]):
            data[f"Quick Win {i+1}"] = qw.title
            data[f"Description & Expected Result {i+1}"] = qw.description or "Automate process to save time."

        # Add Shadow Analysis Insights to report (if it fits the template, or add it to summary)
        if shadow_profile:
            archetype_info = ARCHETYPES.get(shadow_profile.archetype, {})
            shadow_insight = f"Based on our Shadow Analysis of your team's '{shadow_profile.archetype}' patterns, we've identified {archetype_info.get('shadow', ['inefficiencies'])[0]} as a major friction source."
            data["Primary Friction Source"] = shadow_insight
        else:
            data["Primary Friction Source"] = "Manual Data Entry / Task Fragmentation"

        # Special logic to replace the whole table if needed
        template_content = cls.get_template("AUDIT-REPORT-TEMPLATE")
        
        # If we have a lot of processes, we might want to replace the whole table block
        # But for now, we follow the simple [Key] replacement
        
        return cls.generate_report("AUDIT-REPORT-TEMPLATE", data)

    @classmethod
    def save_generated_report(cls, content: str, client_name: str, report_type: str) -> str:
        """Save the generated report to Focus by Kraliki's evidence/reports directory."""
        reports_dir = Path("/home/adminmatej/github/applications/focus-kraliki/evidence/reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{datetime.now().strftime('%Y%m%d')}_{client_name.replace(' ', '_')}_{report_type}.md"
        file_path = reports_dir / filename
        
        with open(file_path, "w") as f:
            f.write(content)
            
        return str(file_path)
