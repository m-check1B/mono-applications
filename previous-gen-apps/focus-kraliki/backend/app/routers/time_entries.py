"""
Time Entries Router - CRUD operations for time tracking
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timedelta
import csv
import io

from app.core.database import get_db
from app.core.security import get_current_user, generate_id
from app.models.user import User
from app.models.time_entry import TimeEntry
from app.models.task import Project, Task
from app.schemas.time_entry import (
    TimeEntryCreate,
    TimeEntryUpdate,
    TimeEntryResponse,
    TimeEntryListResponse,
    TimeEntryStopRequest
)
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/time-entries", tags=["time-tracking"])


@router.get("/", response_model=TimeEntryListResponse)
async def list_time_entries(
    task_id: Optional[str] = Query(None),
    project_id: Optional[str] = Query(None),
    start_date: Optional[str] = Query(None, description="ISO format start date"),
    end_date: Optional[str] = Query(None, description="ISO format end date"),
    limit: int = Query(default=100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List time entries for the current user.

    Can filter by task, project, or date range.
    """
    query = db.query(TimeEntry).filter(TimeEntry.user_id == current_user.id)

    # Apply filters
    if task_id:
        query = query.filter(TimeEntry.task_id == task_id)

    if project_id:
        query = query.filter(TimeEntry.project_id == project_id)

    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        query = query.filter(TimeEntry.start_time >= start_dt)

    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        query = query.filter(TimeEntry.start_time <= end_dt)

    # Order by start time descending (most recent first)
    query = query.order_by(TimeEntry.start_time.desc())

    entries = query.limit(limit).all()
    total = query.count()

    return TimeEntryListResponse(
        entries=[TimeEntryResponse.model_validate(entry) for entry in entries],
        total=total
    )


@router.post("/", response_model=TimeEntryResponse, status_code=201)
async def create_time_entry(
    entry_data: TimeEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new time entry.

    Can be used to start a timer or create a completed entry.
    """
    workspace_id = entry_data.workspace_id
    if not workspace_id:
        if entry_data.task_id:
            task = db.query(Task).filter(Task.id == entry_data.task_id).first()
            if task and task.workspaceId:
                workspace_id = task.workspaceId
        elif entry_data.project_id:
            project = db.query(Project).filter(Project.id == entry_data.project_id).first()
            if project and project.workspaceId:
                workspace_id = project.workspaceId

    if workspace_id:
        WorkspaceService.require_membership(current_user.id, workspace_id, db)
    else:
        workspace = WorkspaceService.ensure_default_workspace(current_user, db)
        workspace_id = workspace.id

    entry = TimeEntry(
        id=generate_id(),
        user_id=current_user.id,
        workspace_id=workspace_id,
        **entry_data.model_dump(exclude_unset=True, exclude={"workspace_id"})
    )

    db.add(entry)
    db.commit()
    db.refresh(entry)

    return TimeEntryResponse.model_validate(entry)


@router.get("/active", response_model=Optional[TimeEntryResponse])
async def get_active_timer(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get currently running timer (entry with no end_time).

    Returns None if no timer is running.
    """
    active_entry = db.query(TimeEntry).filter(
        TimeEntry.user_id == current_user.id,
        TimeEntry.end_time.is_(None)
    ).first()

    if not active_entry:
        return None

    return TimeEntryResponse.model_validate(active_entry)


@router.post("/{entry_id}/stop", response_model=TimeEntryResponse)
async def stop_timer(
    entry_id: str,
    stop_data: TimeEntryStopRequest = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Stop a running timer by setting end_time and calculating duration.
    """
    entry = db.query(TimeEntry).filter(
        TimeEntry.id == entry_id,
        TimeEntry.user_id == current_user.id
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")

    if entry.end_time:
        raise HTTPException(status_code=400, detail="Timer already stopped")

    # Set end time
    end_time = datetime.utcnow()
    if stop_data and stop_data.end_time:
        end_time = stop_data.end_time

    entry.end_time = end_time

    # Calculate duration in seconds
    duration = (entry.end_time - entry.start_time).total_seconds()
    entry.duration_seconds = int(duration)

    # Update description if provided
    if stop_data and stop_data.description:
        entry.description = stop_data.description

    entry.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(entry)

    return TimeEntryResponse.model_validate(entry)


@router.get("/{entry_id}", response_model=TimeEntryResponse)
async def get_time_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a single time entry."""
    entry = db.query(TimeEntry).filter(
        TimeEntry.id == entry_id,
        TimeEntry.user_id == current_user.id
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")

    return TimeEntryResponse.model_validate(entry)


@router.patch("/{entry_id}", response_model=TimeEntryResponse)
async def update_time_entry(
    entry_id: str,
    entry_update: TimeEntryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a time entry."""
    entry = db.query(TimeEntry).filter(
        TimeEntry.id == entry_id,
        TimeEntry.user_id == current_user.id
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")

    update_data = entry_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(entry, key, value)

    # Recalculate duration if times changed
    if entry.start_time and entry.end_time:
        duration = (entry.end_time - entry.start_time).total_seconds()
        entry.duration_seconds = int(duration)

    entry.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(entry)

    return TimeEntryResponse.model_validate(entry)


@router.delete("/{entry_id}")
async def delete_time_entry(
    entry_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a time entry."""
    entry = db.query(TimeEntry).filter(
        TimeEntry.id == entry_id,
        TimeEntry.user_id == current_user.id
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Time entry not found")

    db.delete(entry)
    db.commit()

    return {"success": True, "deletedId": entry_id}


@router.get("/stats/summary")
async def get_time_stats(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get time tracking statistics.

    Returns total time, billable time, entry count, etc.
    """
    query = db.query(TimeEntry).filter(
        TimeEntry.user_id == current_user.id,
        TimeEntry.end_time.isnot(None)  # Only completed entries
    )

    # Apply date filters
    if start_date:
        start_dt = datetime.fromisoformat(start_date)
        query = query.filter(TimeEntry.start_time >= start_dt)

    if end_date:
        end_dt = datetime.fromisoformat(end_date)
        query = query.filter(TimeEntry.start_time <= end_dt)

    entries = query.all()

    # Calculate stats
    total_seconds = sum(entry.duration_seconds or 0 for entry in entries)
    billable_seconds = sum(
        entry.duration_seconds or 0
        for entry in entries
        if entry.billable
    )

    return {
        "total_entries": len(entries),
        "total_hours": round(total_seconds / 3600, 2),
        "billable_hours": round(billable_seconds / 3600, 2),
        "non_billable_hours": round((total_seconds - billable_seconds) / 3600, 2),
        "total_seconds": total_seconds,
        "billable_seconds": billable_seconds
    }


@router.get("/stats/analytics")
async def get_time_analytics(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get detailed time tracking analytics.

    Returns:
    - Total/billable hours
    - Project breakdown
    - Daily average
    - Time by day of week
    - Trends
    """
    query = db.query(TimeEntry).filter(
        TimeEntry.user_id == current_user.id,
        TimeEntry.end_time.isnot(None)
    )

    # Apply date filters
    if start_date:
        query = query.filter(TimeEntry.start_time >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(TimeEntry.start_time <= datetime.fromisoformat(end_date))

    entries = query.all()

    # Calculate totals
    total_seconds = sum(e.duration_seconds or 0 for e in entries)
    billable_seconds = sum(e.duration_seconds or 0 for e in entries if e.billable)

    # Project breakdown
    project_stats = {}
    for entry in entries:
        if entry.project_id:
            project = db.query(Project).filter(Project.id == entry.project_id).first()
            project_name = project.name if project else "Unknown"

            if project_name not in project_stats:
                project_stats[project_name] = {
                    "name": project_name,
                    "hours": 0,
                    "entries": 0
                }

            project_stats[project_name]["hours"] += (entry.duration_seconds or 0) / 3600
            project_stats[project_name]["entries"] += 1

    # Daily average
    if entries:
        date_range = (max(e.start_time for e in entries) - min(e.start_time for e in entries)).days + 1
        daily_average = total_seconds / 3600 / max(date_range, 1)
    else:
        daily_average = 0

    return {
        "totalHours": round(total_seconds / 3600, 2),
        "billableHours": round(billable_seconds / 3600, 2),
        "projectBreakdown": list(project_stats.values()),
        "dailyAverage": round(daily_average, 2),
        "totalEntries": len(entries)
    }


@router.get("/export/csv")
async def export_time_entries_csv(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export time entries to CSV file.

    Columns: Date, Project, Task, Description, Duration (hours), Billable, Rate, Amount
    """
    query = db.query(TimeEntry).filter(
        TimeEntry.user_id == current_user.id,
        TimeEntry.end_time.isnot(None)
    )

    if start_date:
        query = query.filter(TimeEntry.start_time >= datetime.fromisoformat(start_date))
    if end_date:
        query = query.filter(TimeEntry.start_time <= datetime.fromisoformat(end_date))

    entries = query.order_by(TimeEntry.start_time.desc()).all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'Date',
        'Start Time',
        'End Time',
        'Duration (hours)',
        'Project',
        'Task',
        'Description',
        'Billable',
        'Hourly Rate',
        'Amount'
    ])

    # Write data rows
    for entry in entries:
        project_name = ""
        if entry.project_id:
            project = db.query(Project).filter(Project.id == entry.project_id).first()
            if project:
                project_name = project.name

        duration_hours = round((entry.duration_seconds or 0) / 3600, 2)
        hourly_rate = (entry.hourly_rate or 0) / 100  # Convert cents to dollars
        amount = duration_hours * hourly_rate if entry.billable else 0

        writer.writerow([
            entry.start_time.strftime('%Y-%m-%d'),
            entry.start_time.strftime('%H:%M:%S'),
            entry.end_time.strftime('%H:%M:%S') if entry.end_time else '',
            duration_hours,
            project_name,
            entry.task_id or '',
            entry.description or '',
            'Yes' if entry.billable else 'No',
            f'${hourly_rate:.2f}',
            f'${amount:.2f}'
        ])

    # Add summary row
    total_hours = sum((e.duration_seconds or 0) / 3600 for e in entries)
    total_billable = sum(
        ((e.duration_seconds or 0) / 3600) * ((e.hourly_rate or 0) / 100)
        for e in entries
        if e.billable
    )

    writer.writerow([])
    writer.writerow(['TOTAL', '', '', f'{total_hours:.2f}', '', '', '', '', '', f'${total_billable:.2f}'])

    # Return as downloadable file
    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=time-tracking-{datetime.now().strftime('%Y%m%d')}.csv"
        }
    )
