from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.sales_service import SalesService

router = APIRouter(prefix="/sales", tags=["sales"])

class ReportGenerateRequest(BaseModel):
    template_name: str
    client_name: str
    data: Dict[str, Any]

class ReportResponse(BaseModel):
    template_name: str
    client_name: str
    report_content: str
    file_path: Optional[str] = None

@router.get("/templates", response_model=List[str])
async def list_templates(
    current_user: User = Depends(get_current_user)
):
    """List available sales and audit templates."""
    try:
        return SalesService.list_templates()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate", response_model=ReportResponse)
async def generate_sales_report(
    request: ReportGenerateRequest,
    save_to_disk: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a sales report (Audit or Retainer) from a template.
    """
    try:
        report_content = SalesService.generate_report(request.template_name, request.data)
        
        file_path = None
        if save_to_disk:
            file_path = SalesService.save_generated_report(
                report_content, 
                request.client_name, 
                request.template_name
            )
            
        return ReportResponse(
            template_name=request.template_name,
            client_name=request.client_name,
            report_content=report_content,
            file_path=file_path
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audit/{project_id}", response_model=ReportResponse)
async def generate_automated_audit(
    project_id: str,
    save_to_disk: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Automate the generation of an Audit Report for a specific project.
    
    This pulls data from tasks (human/ai cost insights) and Shadow Analysis
    to build a comprehensive Reality Check report.
    """
    try:
        report_content = await SalesService.generate_automated_audit(
            db, 
            current_user.id, 
            project_id
        )
        
        # Get project name for filename
        from app.models.task import Project
        project = db.query(Project).filter(Project.id == project_id).first()
        client_name = project.name if project else "Unknown_Client"
        
        file_path = None
        if save_to_disk:
            file_path = SalesService.save_generated_report(
                report_content, 
                client_name, 
                "AUTOMATED-AUDIT"
            )
            
        return ReportResponse(
            template_name="AUDIT-REPORT-TEMPLATE",
            client_name=client_name,
            report_content=report_content,
            file_path=file_path
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
