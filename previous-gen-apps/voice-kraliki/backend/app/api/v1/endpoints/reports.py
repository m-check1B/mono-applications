"""
Reports API Endpoints

REST API for report templates, generation, scheduling, and delivery.
"""

from datetime import UTC, datetime

from app.database import get_db
from app.models.report import (
    Report,
    ReportCreate,
    ReportFormat,
    ReportResponse,
    ReportSchedule,
    ReportScheduleCreate,
    ReportScheduleResponse,
    ReportStatus,
    ReportTemplate,
    ReportTemplateCreate,
    ReportTemplateResponse,
)
from app.services.analytics import ReportGeneratorService
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/reports", tags=["reports"])


# ============================================================================
# Report Templates Endpoints
# ============================================================================

@router.post("/templates", response_model=ReportTemplateResponse)
def create_template(
    template: ReportTemplateCreate,
    db: Session = Depends(get_db)
):
    """Create a new report template"""
    db_template = ReportTemplate(
        name=template.name,
        description=template.description,
        report_type=template.report_type.value,
        configuration=template.configuration,
        default_format=template.default_format.value,
        is_public=template.is_public,
        team_id=template.team_id,
        tags=template.tags
    )

    db.add(db_template)
    db.commit()
    db.refresh(db_template)

    return db_template


@router.get("/templates", response_model=list[ReportTemplateResponse])
def get_templates(
    report_type: str | None = None,
    is_public: bool | None = None,
    team_id: int | None = None,
    is_active: bool | None = True,
    db: Session = Depends(get_db)
):
    """Get report templates"""
    query = db.query(ReportTemplate)

    if report_type:
        query = query.filter(ReportTemplate.report_type == report_type)
    if is_public is not None:
        query = query.filter(ReportTemplate.is_public == is_public)
    if is_active is not None:
        query = query.filter(ReportTemplate.is_active == is_active)
    if team_id:
        query = query.filter(
            (ReportTemplate.team_id == team_id) | (ReportTemplate.is_public == True)
        )

    return query.all()


@router.get("/templates/{template_id}", response_model=ReportTemplateResponse)
def get_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific report template"""
    template = db.query(ReportTemplate).filter(
        ReportTemplate.id == template_id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return template


@router.put("/templates/{template_id}", response_model=ReportTemplateResponse)
def update_template(
    template_id: int,
    template: ReportTemplateCreate,
    db: Session = Depends(get_db)
):
    """Update a report template"""
    db_template = db.query(ReportTemplate).filter(
        ReportTemplate.id == template_id
    ).first()

    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")

    db_template.name = template.name
    db_template.description = template.description
    db_template.configuration = template.configuration
    db_template.default_format = template.default_format.value
    db_template.is_public = template.is_public
    db_template.tags = template.tags
    db_template.version += 1
    db_template.updated_at = datetime.now(UTC)

    db.commit()
    db.refresh(db_template)

    return db_template


@router.delete("/templates/{template_id}")
def delete_template(
    template_id: int,
    db: Session = Depends(get_db)
):
    """Delete a report template"""
    template = db.query(ReportTemplate).filter(
        ReportTemplate.id == template_id
    ).first()

    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    # Soft delete by marking inactive
    template.is_active = False
    template.updated_at = datetime.now(UTC)

    db.commit()

    return {"status": "deleted", "id": template_id}


# ============================================================================
# Reports Endpoints
# ============================================================================

@router.post("/generate", response_model=ReportResponse)
def generate_report(
    report: ReportCreate,
    requested_by_id: int | None = None,
    db: Session = Depends(get_db)
):
    """Generate a report from template"""
    service = ReportGeneratorService(db)

    if not report.template_id:
        raise HTTPException(status_code=400, detail="template_id is required")

    return service.generate_report(
        template_id=report.template_id,
        filters=report.filters,
        format=report.format,
        requested_by_id=requested_by_id
    )


@router.get("/", response_model=list[ReportResponse])
def get_reports(
    report_type: str | None = None,
    status: str | None = None,
    team_id: int | None = None,
    campaign_id: int | None = None,
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
    limit: int = Query(100, le=1000),
    db: Session = Depends(get_db)
):
    """Get generated reports"""
    query = db.query(Report).filter(Report.is_deleted == False)

    if report_type:
        query = query.filter(Report.report_type == report_type)
    if status:
        query = query.filter(Report.status == status)
    if team_id:
        query = query.filter(Report.team_id == team_id)
    if campaign_id:
        query = query.filter(Report.campaign_id == campaign_id)
    if start_date:
        query = query.filter(Report.requested_at >= start_date)
    if end_date:
        query = query.filter(Report.requested_at <= end_date)

    return query.order_by(Report.requested_at.desc()).limit(limit).all()


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific report"""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.is_deleted == False
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    return report


@router.get("/{report_id}/data")
def get_report_data(
    report_id: int,
    db: Session = Depends(get_db)
):
    """Get report data (JSON format)"""
    report = db.query(Report).filter(
        Report.id == report_id,
        Report.is_deleted == False
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    if report.status != ReportStatus.COMPLETED.value:
        raise HTTPException(
            status_code=400,
            detail=f"Report is not completed (status: {report.status})"
        )

    return report.report_data


@router.delete("/{report_id}")
def delete_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """Delete a report"""
    report = db.query(Report).filter(
        Report.id == report_id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    report.is_deleted = True
    report.deleted_at = datetime.now(UTC)

    db.commit()

    return {"status": "deleted", "id": report_id}


# ============================================================================
# Report Schedules Endpoints
# ============================================================================

@router.post("/schedules", response_model=ReportScheduleResponse)
def create_schedule(
    schedule: ReportScheduleCreate,
    created_by_id: int | None = None,
    db: Session = Depends(get_db)
):
    """Create a report schedule"""
    db_schedule = ReportSchedule(
        name=schedule.name,
        description=schedule.description,
        template_id=schedule.template_id,
        format=schedule.format.value,
        filters=schedule.filters,
        parameters=schedule.parameters,
        frequency=schedule.frequency.value,
        cron_expression=schedule.cron_expression,
        hour=schedule.hour,
        day_of_week=schedule.day_of_week,
        day_of_month=schedule.day_of_month,
        timezone=schedule.timezone,
        delivery_methods=schedule.delivery_methods,
        delivery_config=schedule.delivery_config,
        team_id=schedule.team_id,
        created_by_id=created_by_id
    )

    # Calculate next run time
    # (Simplified - in production, use proper scheduling library)
    db_schedule.next_run_at = datetime.now(UTC)

    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)

    return db_schedule


@router.get("/schedules", response_model=list[ReportScheduleResponse])
def get_schedules(
    is_active: bool | None = None,
    template_id: int | None = None,
    team_id: int | None = None,
    db: Session = Depends(get_db)
):
    """Get report schedules"""
    query = db.query(ReportSchedule)

    if is_active is not None:
        query = query.filter(ReportSchedule.is_active == is_active)
    if template_id:
        query = query.filter(ReportSchedule.template_id == template_id)
    if team_id:
        query = query.filter(ReportSchedule.team_id == team_id)

    return query.all()


@router.get("/schedules/{schedule_id}", response_model=ReportScheduleResponse)
def get_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific report schedule"""
    schedule = db.query(ReportSchedule).filter(
        ReportSchedule.id == schedule_id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    return schedule


@router.put("/schedules/{schedule_id}", response_model=ReportScheduleResponse)
def update_schedule(
    schedule_id: int,
    schedule: ReportScheduleCreate,
    db: Session = Depends(get_db)
):
    """Update a report schedule"""
    db_schedule = db.query(ReportSchedule).filter(
        ReportSchedule.id == schedule_id
    ).first()

    if not db_schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    db_schedule.name = schedule.name
    db_schedule.description = schedule.description
    db_schedule.filters = schedule.filters
    db_schedule.frequency = schedule.frequency.value
    db_schedule.hour = schedule.hour
    db_schedule.day_of_week = schedule.day_of_week
    db_schedule.day_of_month = schedule.day_of_month
    db_schedule.delivery_methods = schedule.delivery_methods
    db_schedule.delivery_config = schedule.delivery_config
    db_schedule.updated_at = datetime.now(UTC)

    db.commit()
    db.refresh(db_schedule)

    return db_schedule


@router.delete("/schedules/{schedule_id}")
def delete_schedule(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """Delete a report schedule"""
    schedule = db.query(ReportSchedule).filter(
        ReportSchedule.id == schedule_id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # Deactivate instead of delete
    schedule.is_active = False
    schedule.updated_at = datetime.now(UTC)

    db.commit()

    return {"status": "deleted", "id": schedule_id}


@router.post("/schedules/{schedule_id}/run")
def run_schedule_now(
    schedule_id: int,
    db: Session = Depends(get_db)
):
    """Trigger a scheduled report to run immediately"""
    schedule = db.query(ReportSchedule).filter(
        ReportSchedule.id == schedule_id
    ).first()

    if not schedule:
        raise HTTPException(status_code=404, detail="Schedule not found")

    # Generate report using the schedule's configuration
    service = ReportGeneratorService(db)

    report = service.generate_report(
        template_id=schedule.template_id,
        filters=schedule.filters,
        format=ReportFormat(schedule.format)
    )

    # Update schedule tracking
    schedule.last_run_at = datetime.now(UTC)
    schedule.last_report_id = report.id
    schedule.last_status = report.status
    schedule.run_count += 1

    db.commit()

    return report
