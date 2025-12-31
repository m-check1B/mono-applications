"""
Export Router - Invoice and billable hours export functionality for freelancers
Addresses CR-001 from BACKLOG.md (P0: Critical for Freelancer segment)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Optional, Literal
from datetime import datetime, timedelta
import csv
import io
import json

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.time_entry import TimeEntry
from app.models.task import Project, Task
from app.models.shadow_profile import ShadowProfile, ShadowInsight
from pydantic import BaseModel, Field
import os

# PDF generation imports
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False


router = APIRouter(prefix="/exports", tags=["exports"])


class InvoiceExportRequest(BaseModel):
    """Request model for invoice export"""
    start_date: str = Field(..., description="Start date in ISO format (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date in ISO format (YYYY-MM-DD)")
    project_id: Optional[str] = Field(None, description="Filter by project ID")
    client_name: Optional[str] = Field(None, description="Client name for invoice")
    invoice_number: Optional[str] = Field(None, description="Invoice number")
    hourly_rate: Optional[float] = Field(None, description="Override hourly rate (USD)")
    format: Literal["csv", "json", "pdf"] = Field("csv", description="Export format")
    include_non_billable: bool = Field(False, description="Include non-billable time")


class BillableHoursSummary(BaseModel):
    """Summary of billable hours"""
    total_hours: float
    billable_hours: float
    non_billable_hours: float
    total_amount: float
    currency: str = "USD"
    projects: list[dict]
    date_range: dict


class AuditExportRequest(BaseModel):
    """Request model for Reality Check Audit report generation"""
    client_name: str = Field(..., description="Client name for the report")
    start_date: Optional[str] = Field(None, description="Analysis start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="Analysis end date (YYYY-MM-DD)")
    hourly_rate: float = Field(50.0, description="Estimated hourly rate for savings calculation")
    format: Literal["md", "pdf"] = Field("md", description="Export format")


@router.post("/audit/generate")
async def generate_audit_report(
    request: AuditExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a 'Reality Check' Audit Report.
    Integrates Shadow Analysis and Task Data with AUDIT-REPORT-TEMPLATE.md.
    """
    # 1. Fetch User Shadow Profile
    shadow_profile = db.query(ShadowProfile).filter(ShadowProfile.user_id == current_user.id).first()
    if not shadow_profile:
        # Create a default profile if none exists
        from app.services.shadow_analyzer import ShadowAnalyzerService
        analyzer = ShadowAnalyzerService(db)
        await analyzer.create_profile(current_user.id)
        shadow_profile = db.query(ShadowProfile).filter(ShadowProfile.user_id == current_user.id).first()

    # 2. Fetch Tasks for analysis
    tasks_query = db.query(Task).filter(Task.userId == current_user.id)
    if request.start_date:
        tasks_query = tasks_query.filter(Task.createdAt >= datetime.fromisoformat(request.start_date))
    tasks = tasks_query.all()

    # 3. Analyze "Manual Tax"
    # Identify repetitive tasks (tasks with similar titles or multiple occurrences)
    repetitive_tasks = {}
    for task in tasks:
        title_key = (task.title or "").lower().strip()
        if title_key in repetitive_tasks:
            repetitive_tasks[title_key]["count"] += 1
            repetitive_tasks[title_key]["total_estimated"] += task.estimatedMinutes or 30
        else:
            repetitive_tasks[title_key] = {
                "title": task.title,
                "count": 1,
                "total_estimated": task.estimatedMinutes or 30
            }

    # Sort by total estimated time
    sorted_repetitive = sorted(repetitive_tasks.values(), key=lambda x: x["total_estimated"], reverse=True)
    top_friction_tasks = sorted_repetitive[:3]

    # Calculate savings
    total_friction_mins = sum(t["total_estimated"] for t in top_friction_tasks)
    weekly_friction_hours = (total_friction_mins / 60) * 4  # Extrapolate if needed, assuming tasks are over a month
    annual_savings = weekly_friction_hours * 52 * request.hourly_rate * 0.8  # Assume 80% automation efficiency

    # 4. Load Template
    template_path = os.path.join(os.getcwd(), "../../brain-2026/sales/AUDIT-REPORT-TEMPLATE.md")
    if not os.path.exists(template_path):
        # Fallback to local copy or hardcoded string if path is different
        template_content = """# Reality Check Audit Report: [Client Name]
**Date:** [Date]
**Auditor:** Verduona AI Swarm (by Kraliki)

## 1. Executive Summary
We performed a 60-minute diagnostic of [Client Name]'s operations. 
**Total Identified Annual Savings:** €[Amount]
**Primary Friction Source:** [Primary Friction Source]

## 2. The "Manual Tax" Breakdown
| Process | Current Cost (Annual) | AI Agent Cost (Annual) | Arbitrage Ratio |
| :--- | :--- | :--- | :--- |
| [Process 1] | €[Cost 1] | €[AI Cost 1] | [Ratio 1]x |
| [Process 2] | €[Cost 2] | €[AI Cost 2] | [Ratio 2]x |
| [Process 3] | €[Cost 3] | €[AI Cost 3] | [Ratio 3]x |

## 3. Top 3 "Quick Win" Automations
1. **[Quick Win 1]**
2. **[Quick Win 2]**
3. **[Quick Win 3]**

## 4. Next Steps
- Pilot Goal: Automate [Most High Impact Process]
- Timeline: 2 Weeks
- Fixed Fee: €2,500
"""
    else:
        with open(template_path, 'r') as f:
            template_content = f.read()

    # 5. Populate Template
    archetype_friction = {
        "warrior": "Rigidity and Control Issues",
        "sage": "Overthinking and Analysis Paralysis",
        "lover": "Boundary and Dependency Issues",
        "creator": "Perfectionism and Procrastination",
        "caregiver": "Self-Neglect and Burnout",
        "explorer": "Restlessness and Lack of Commitment"
    }

    primary_friction = archetype_friction.get(shadow_profile.archetype, "Manual Data Plumbing")

    report = template_content.replace("[Client Name]", request.client_name)
    report = report.replace("[Date]", datetime.now().strftime('%Y-%m-%d'))
    report = report.replace("[Amount]", f"{annual_savings:,.2f}")
    report = report.replace("[Primary Friction Source]", primary_friction)

    for i, t in enumerate(top_friction_tasks, 1):
        cost = (t["total_estimated"] / 60) * request.hourly_rate * 52 / 4 # Annualized
        ai_cost = cost * 0.05 # Assume 95% reduction
        ratio = 20
        
        report = report.replace(f"[Process {i}]", t["title"])
        report = report.replace(f"€[Cost {i}]", f"€{cost:,.2f}")
        report = report.replace(f"€[AI Cost {i}]", f"€{ai_cost:,.2f}")
        report = report.replace(f"[Ratio {i}]x", f"{ratio}x")
        
        # Quick wins
        report = report.replace(f"[Quick Win {i}]:", f"Automate {t['title']}:")
        report = report.replace(f"[Description & Expected Result {i}]", f"Deploy AI agent to handle {t['title']} reducing manual labor by 90%.")

    report = report.replace("[Number]", "10")
    report = report.replace("[Rate]", str(request.hourly_rate))
    report = report.replace("[Most High Impact Process]", top_friction_tasks[0]["title"] if top_friction_tasks else "Manual Data Pipeline")

    if request.format == "md":
        return StreamingResponse(
            iter([report]),
            media_type="text/markdown",
            headers={
                "Content-Disposition": f"attachment; filename=audit-report-{request.client_name.replace(' ', '-')}.md"
            }
        )
    elif request.format == "pdf":
        # PDF generation would follow a similar logic to generate_invoice but with the report content
        # For now, return MD or simple PDF
        if not PDF_AVAILABLE:
            raise HTTPException(status_code=503, detail="PDF export unavailable")
        
        # (Simplified PDF generation omitted for brevity, would use similar elements as above)
        return StreamingResponse(
            iter([report]), # Placeholder
            media_type="text/markdown"
        )

    return {"status": "success", "report": report}


@router.post("/invoices/generate")
async def generate_invoice(
    request: InvoiceExportRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate an invoice based on billable hours.

    This is a critical feature for freelancers (CR-001):
    - Export billable hours with client breakdown
    - Support CSV, JSON, and PDF formats
    - Include project/task details
    - Calculate total amounts based on hourly rates

    Usage:
    POST /exports/invoices/generate
    {
      "start_date": "2025-11-01",
      "end_date": "2025-11-30",
      "client_name": "Acme Corp",
      "invoice_number": "INV-2025-001",
      "hourly_rate": 75.00,
      "format": "csv"
    }
    """
    # Parse dates
    try:
        start_dt = datetime.fromisoformat(request.start_date)
        end_dt = datetime.fromisoformat(request.end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Query time entries
    query = db.query(TimeEntry).filter(
        TimeEntry.user_id == current_user.id,
        TimeEntry.end_time.isnot(None),  # Only completed entries
        TimeEntry.start_time >= start_dt,
        TimeEntry.start_time <= end_dt
    )

    if request.project_id:
        query = query.filter(TimeEntry.project_id == request.project_id)

    if not request.include_non_billable:
        query = query.filter(TimeEntry.billable == True)

    entries = query.order_by(TimeEntry.start_time).all()

    if not entries:
        raise HTTPException(status_code=404, detail="No billable hours found for this period")

    # Group by project
    projects_data = {}
    total_seconds = 0
    total_billable_seconds = 0

    for entry in entries:
        project_id = entry.project_id or "no-project"
        project_name = "No Project"

        if entry.project_id:
            project = db.query(Project).filter(Project.id == entry.project_id).first()
            if project:
                project_name = project.name

        if project_id not in projects_data:
            projects_data[project_id] = {
                "project_id": project_id,
                "project_name": project_name,
                "entries": [],
                "total_hours": 0,
                "total_amount": 0
            }

        duration_hours = (entry.duration_seconds or 0) / 3600

        # Use override rate, entry rate, or default
        hourly_rate = request.hourly_rate or ((entry.hourly_rate or 0) / 100)
        amount = duration_hours * hourly_rate if entry.billable else 0

        projects_data[project_id]["entries"].append({
            "date": entry.start_time.strftime('%Y-%m-%d'),
            "start_time": entry.start_time.strftime('%H:%M'),
            "end_time": entry.end_time.strftime('%H:%M') if entry.end_time else '',
            "duration_hours": round(duration_hours, 2),
            "description": entry.description or "",
            "task_id": entry.task_id or "",
            "billable": entry.billable is True,
            "hourly_rate": hourly_rate,
            "amount": round(amount, 2)
        })

        projects_data[project_id]["total_hours"] += duration_hours
        projects_data[project_id]["total_amount"] += amount

        total_seconds += entry.duration_seconds or 0
        if entry.billable:
            total_billable_seconds += entry.duration_seconds or 0

    # Generate output based on format
    if request.format == "json":
        return JSONResponse(content={
            "invoice": {
                "invoice_number": request.invoice_number or f"INV-{datetime.now().strftime('%Y%m%d')}",
                "client_name": request.client_name or "Client",
                "invoice_date": datetime.now().strftime('%Y-%m-%d'),
                "period_start": request.start_date,
                "period_end": request.end_date,
                "freelancer": {
                    "name": current_user.username or current_user.email,
                    "email": current_user.email
                }
            },
            "summary": {
                "total_hours": round(total_seconds / 3600, 2),
                "billable_hours": round(total_billable_seconds / 3600, 2),
                "non_billable_hours": round((total_seconds - total_billable_seconds) / 3600, 2),
                "total_amount": sum(p["total_amount"] for p in projects_data.values()),
                "currency": "USD"
            },
            "projects": [
                {
                    "project_name": p["project_name"],
                    "total_hours": round(p["total_hours"], 2),
                    "total_amount": round(p["total_amount"], 2),
                    "entries": p["entries"]
                }
                for p in projects_data.values()
            ]
        })

    elif request.format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)

        # Invoice header
        invoice_number = request.invoice_number or f"INV-{datetime.now().strftime('%Y%m%d')}"
        client_name = request.client_name or "Client"

        writer.writerow(['INVOICE'])
        writer.writerow(['Invoice Number:', invoice_number])
        writer.writerow(['Client:', client_name])
        writer.writerow(['Invoice Date:', datetime.now().strftime('%Y-%m-%d')])
        writer.writerow(['Period:', f"{request.start_date} to {request.end_date}"])
        writer.writerow(['From:', current_user.username or current_user.email])
        writer.writerow([])

        # Column headers
        writer.writerow([
            'Date', 'Start', 'End', 'Duration (hrs)',
            'Project', 'Description', 'Billable', 'Rate', 'Amount'
        ])

        # Entries grouped by project
        for project_data in projects_data.values():
            for entry in project_data["entries"]:
                writer.writerow([
                    entry["date"],
                    entry["start_time"],
                    entry["end_time"],
                    entry["duration_hours"],
                    project_data["project_name"],
                    entry["description"],
                    'Yes' if entry["billable"] else 'No',
                    f'${entry["hourly_rate"]:.2f}',
                    f'${entry["amount"]:.2f}'
                ])

        # Summary
        writer.writerow([])
        writer.writerow(['SUMMARY'])
        writer.writerow(['Total Hours:', round(total_seconds / 3600, 2)])
        writer.writerow(['Billable Hours:', round(total_billable_seconds / 3600, 2)])
        writer.writerow(['Total Amount:', f'${sum(p["total_amount"] for p in projects_data.values()):.2f}'])

        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=invoice-{invoice_number}-{datetime.now().strftime('%Y%m%d')}.csv"
            }
        )

    elif request.format == "pdf":
        if not PDF_AVAILABLE:
            raise HTTPException(
                status_code=503,
                detail="PDF export unavailable. Install reportlab: pip install reportlab"
            )

        # Generate PDF invoice
        output = io.BytesIO()
        doc = SimpleDocTemplate(
            output,
            pagesize=letter,
            rightMargin=0.5 * inch,
            leftMargin=0.5 * inch,
            topMargin=0.5 * inch,
            bottomMargin=0.5 * inch
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=20
        )
        header_style = ParagraphStyle(
            'InvoiceHeader',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=5
        )

        elements = []

        # Invoice header
        invoice_number = request.invoice_number or f"INV-{datetime.now().strftime('%Y%m%d')}"
        client_name = request.client_name or "Client"

        elements.append(Paragraph("INVOICE", title_style))
        elements.append(Paragraph(f"<b>Invoice Number:</b> {invoice_number}", header_style))
        elements.append(Paragraph(f"<b>Client:</b> {client_name}", header_style))
        elements.append(Paragraph(f"<b>Invoice Date:</b> {datetime.now().strftime('%Y-%m-%d')}", header_style))
        elements.append(Paragraph(f"<b>Period:</b> {request.start_date} to {request.end_date}", header_style))
        elements.append(Paragraph(f"<b>From:</b> {current_user.username or current_user.email}", header_style))
        elements.append(Spacer(1, 20))

        # Build table data
        table_data = [['Date', 'Project', 'Description', 'Hours', 'Rate', 'Amount']]

        for project_data in projects_data.values():
            for entry in project_data["entries"]:
                table_data.append([
                    entry["date"],
                    project_data["project_name"][:20],  # Truncate long names
                    (entry["description"] or "")[:30],  # Truncate descriptions
                    f"{entry['duration_hours']:.2f}",
                    f"${entry['hourly_rate']:.2f}",
                    f"${entry['amount']:.2f}"
                ])

        # Create and style the table
        table = Table(table_data, colWidths=[1*inch, 1.2*inch, 2*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#333333')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f5f5')),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),  # Right-align numbers
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

        # Summary section
        total_amount = sum(p["total_amount"] for p in projects_data.values())
        summary_data = [
            ['Total Hours:', f"{round(total_seconds / 3600, 2)} hrs"],
            ['Billable Hours:', f"{round(total_billable_seconds / 3600, 2)} hrs"],
            ['', ''],
            ['TOTAL AMOUNT:', f"${total_amount:.2f}"]
        ]

        summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#333333')),
            ('LINEABOVE', (0, -1), (-1, -1), 1, colors.black),
        ]))
        elements.append(summary_table)

        # Build the PDF
        doc.build(elements)
        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=invoice-{invoice_number}-{datetime.now().strftime('%Y%m%d')}.pdf"
            }
        )

    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")


@router.get("/billable/summary", response_model=BillableHoursSummary)
async def get_billable_summary(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    project_id: Optional[str] = Query(None, description="Filter by project"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a summary of billable hours for a date range.

    This endpoint provides quick insights for freelancers:
    - Total vs billable hours breakdown
    - Project-level summaries
    - Revenue calculations

    Usage:
    GET /exports/billable/summary?start_date=2025-11-01&end_date=2025-11-30
    """
    try:
        start_dt = datetime.fromisoformat(start_date)
        end_dt = datetime.fromisoformat(end_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")

    query = db.query(TimeEntry).filter(
        TimeEntry.user_id == current_user.id,
        TimeEntry.end_time.isnot(None),
        TimeEntry.start_time >= start_dt,
        TimeEntry.start_time <= end_dt
    )

    if project_id:
        query = query.filter(TimeEntry.project_id == project_id)

    entries = query.all()

    # Calculate totals
    total_seconds = sum(e.duration_seconds or 0 for e in entries)
    billable_seconds = sum(e.duration_seconds or 0 for e in entries if e.billable)

    total_amount = 0
    projects = {}

    for entry in entries:
        if entry.billable:
            duration_hours = (entry.duration_seconds or 0) / 3600
            hourly_rate = (entry.hourly_rate or 0) / 100
            total_amount += duration_hours * hourly_rate

        # Group by project
        project_id_key = entry.project_id or "no-project"
        if project_id_key not in projects:
            project_name = "No Project"
            if entry.project_id:
                project = db.query(Project).filter(Project.id == entry.project_id).first()
                if project:
                    project_name = project.name

            projects[project_id_key] = {
                "project_id": project_id_key,
                "project_name": project_name,
                "total_hours": 0,
                "billable_hours": 0,
                "total_amount": 0
            }

        duration_hours = (entry.duration_seconds or 0) / 3600
        projects[project_id_key]["total_hours"] += duration_hours

        if entry.billable:
            projects[project_id_key]["billable_hours"] += duration_hours
            hourly_rate = (entry.hourly_rate or 0) / 100
            projects[project_id_key]["total_amount"] += duration_hours * hourly_rate

    return BillableHoursSummary(
        total_hours=round(total_seconds / 3600, 2),
        billable_hours=round(billable_seconds / 3600, 2),
        non_billable_hours=round((total_seconds - billable_seconds) / 3600, 2),
        total_amount=round(total_amount, 2),
        currency="USD",
        projects=[
            {
                "project_id": p["project_id"],
                "project_name": p["project_name"],
                "total_hours": round(p["total_hours"], 2),
                "billable_hours": round(p["billable_hours"], 2),
                "total_amount": round(p["total_amount"], 2)
            }
            for p in projects.values()
        ],
        date_range={
            "start": start_date,
            "end": end_date
        }
    )


@router.get("/billable/weekly")
async def get_weekly_billable(
    weeks: int = Query(4, ge=1, le=52, description="Number of weeks to look back"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get weekly breakdown of billable hours for the past N weeks.

    Helps freelancers track trends and plan invoicing cycles.

    Usage:
    GET /exports/billable/weekly?weeks=4
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(weeks=weeks)

    query = db.query(TimeEntry).filter(
        TimeEntry.user_id == current_user.id,
        TimeEntry.end_time.isnot(None),
        TimeEntry.start_time >= start_date,
        TimeEntry.start_time <= end_date
    )

    entries = query.all()

    # Group by week
    weekly_data = {}

    for entry in entries:
        # Get week start (Monday)
        week_start = entry.start_time - timedelta(days=entry.start_time.weekday())
        week_key = week_start.strftime('%Y-%m-%d')

        if week_key not in weekly_data:
            weekly_data[week_key] = {
                "week_start": week_key,
                "total_hours": 0,
                "billable_hours": 0,
                "total_amount": 0
            }

        duration_hours = (entry.duration_seconds or 0) / 3600
        weekly_data[week_key]["total_hours"] += duration_hours

        if entry.billable:
            weekly_data[week_key]["billable_hours"] += duration_hours
            hourly_rate = (entry.hourly_rate or 0) / 100
            weekly_data[week_key]["total_amount"] += duration_hours * hourly_rate

    # Convert to sorted list
    weekly_breakdown = sorted(
        [
            {
                "week_start": w["week_start"],
                "total_hours": round(w["total_hours"], 2),
                "billable_hours": round(w["billable_hours"], 2),
                "total_amount": round(w["total_amount"], 2)
            }
            for w in weekly_data.values()
        ],
        key=lambda x: x["week_start"]
    )

    return {
        "weeks": weekly_breakdown,
        "summary": {
            "total_weeks": len(weekly_breakdown),
            "average_billable_hours": round(
                sum(w["billable_hours"] for w in weekly_breakdown) / max(len(weekly_breakdown), 1), 2
            ),
            "average_weekly_revenue": round(
                sum(w["total_amount"] for w in weekly_breakdown) / max(len(weekly_breakdown), 1), 2
            )
        }
    }
