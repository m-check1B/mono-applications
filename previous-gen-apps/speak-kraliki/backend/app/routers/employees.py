"""
Speak by Kraliki - Employees Router
Employee management for survey targeting

RBAC enforced:
- owner, hr_director: Full access, all departments
- manager: View/update only their department employees
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, ConfigDict, EmailStr

from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.rbac import (
    Permission,
    require_permission,
    department_scope,
    verify_department_access,
)
from app.models.employee import Employee
from app.models.department import Department

router = APIRouter(prefix="/speak/employees", tags=["employees"])


class EmployeeCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str | None = None
    department_id: UUID | None = None
    job_title: str | None = None


class EmployeeUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    phone: str | None = None
    department_id: UUID | None = None
    job_title: str | None = None
    is_active: bool | None = None
    vop_opted_out: bool | None = None


class EmployeeResponse(BaseModel):
    id: UUID
    company_id: UUID
    department_id: UUID | None
    first_name: str
    last_name: str
    email: str
    phone: str | None
    job_title: str | None
    is_active: bool
    vop_opted_out: bool
    vop_participation_rate: float | None

    model_config = ConfigDict(from_attributes=True)


class DepartmentCreate(BaseModel):
    name: str
    parent_id: UUID | None = None


class DepartmentResponse(BaseModel):
    id: UUID
    company_id: UUID
    name: str
    parent_id: UUID | None
    employee_count: int = 0

    model_config = ConfigDict(from_attributes=True)


@router.get("", response_model=list[EmployeeResponse])
async def list_employees(
    department_id: UUID | None = None,
    include_inactive: bool = False,
    current_user: dict = Depends(require_permission(Permission.EMPLOYEES_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """List employees for the company.

    RBAC: Managers only see their department's employees.
    """
    company_id = UUID(current_user["company_id"])

    query = select(Employee).where(Employee.company_id == company_id)

    # Apply department scoping based on role
    query = department_scope(query, current_user, Employee)

    # Additional filter if specific department requested
    if department_id:
        # Verify user can access this department
        if not verify_department_access(current_user, department_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this department"
            )
        query = query.where(Employee.department_id == department_id)

    if not include_inactive:
        query = query.where(Employee.is_active == True)

    query = query.order_by(Employee.last_name, Employee.first_name)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=EmployeeResponse)
async def create_employee(
    request: EmployeeCreate,
    current_user: dict = Depends(require_permission(Permission.EMPLOYEES_CREATE)),
    db: AsyncSession = Depends(get_db)
):
    """Create new employee.

    RBAC: Only owner and hr_director can create employees.
    """
    company_id = UUID(current_user["company_id"])

    # Check email uniqueness within company
    existing = await db.execute(
        select(Employee)
        .where(Employee.company_id == company_id)
        .where(Employee.email == request.email)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee with this email already exists"
        )

    employee = Employee(
        company_id=company_id,
        first_name=request.first_name,
        last_name=request.last_name,
        email=request.email,
        phone=request.phone,
        department_id=request.department_id,
        job_title=request.job_title,
    )
    db.add(employee)
    await db.commit()
    await db.refresh(employee)

    return employee


@router.get("/{employee_id}", response_model=EmployeeResponse)
async def get_employee(
    employee_id: UUID,
    current_user: dict = Depends(require_permission(Permission.EMPLOYEES_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """Get employee details.

    RBAC: Managers can only view employees in their department.
    """
    company_id = UUID(current_user["company_id"])

    result = await db.execute(
        select(Employee)
        .where(Employee.id == employee_id)
        .where(Employee.company_id == company_id)
    )
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    # Verify department access for managers
    if not verify_department_access(current_user, employee.department_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this employee"
        )

    return employee


@router.patch("/{employee_id}", response_model=EmployeeResponse)
async def update_employee(
    employee_id: UUID,
    request: EmployeeUpdate,
    current_user: dict = Depends(require_permission(Permission.EMPLOYEES_UPDATE)),
    db: AsyncSession = Depends(get_db)
):
    """Update employee.

    RBAC: Only owner and hr_director can update employees.
    """
    company_id = UUID(current_user["company_id"])

    result = await db.execute(
        select(Employee)
        .where(Employee.id == employee_id)
        .where(Employee.company_id == company_id)
    )
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(employee, field, value)

    await db.commit()
    await db.refresh(employee)

    return employee


@router.delete("/{employee_id}")
async def delete_employee(
    employee_id: UUID,
    current_user: dict = Depends(require_permission(Permission.EMPLOYEES_DELETE)),
    db: AsyncSession = Depends(get_db)
):
    """Delete employee (soft delete - sets inactive).

    RBAC: Only owner and hr_director can delete employees.
    """
    company_id = UUID(current_user["company_id"])

    result = await db.execute(
        select(Employee)
        .where(Employee.id == employee_id)
        .where(Employee.company_id == company_id)
    )
    employee = result.scalar_one_or_none()

    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employee not found"
        )

    employee.is_active = False
    await db.commit()

    return {"message": "Employee deactivated"}


# Department endpoints

@router.get("/departments/list", response_model=list[DepartmentResponse])
async def list_departments(
    current_user: dict = Depends(require_permission(Permission.DEPARTMENTS_VIEW)),
    db: AsyncSession = Depends(get_db)
):
    """List departments for the company."""
    company_id = UUID(current_user["company_id"])

    result = await db.execute(
        select(Department)
        .where(Department.company_id == company_id)
        .order_by(Department.name)
    )
    departments = result.scalars().all()

    # Add employee counts
    responses = []
    for dept in departments:
        from sqlalchemy import func
        count = await db.scalar(
            select(func.count(Employee.id))
            .where(Employee.department_id == dept.id)
            .where(Employee.is_active == True)
        )
        response = DepartmentResponse.model_validate(dept)
        response.employee_count = count or 0
        responses.append(response)

    return responses


@router.post("/departments", response_model=DepartmentResponse)
async def create_department(
    request: DepartmentCreate,
    current_user: dict = Depends(require_permission(Permission.DEPARTMENTS_CREATE)),
    db: AsyncSession = Depends(get_db)
):
    """Create new department.

    RBAC: Only owner and hr_director can create departments.
    """
    company_id = UUID(current_user["company_id"])

    department = Department(
        company_id=company_id,
        name=request.name,
        parent_id=request.parent_id,
    )
    db.add(department)
    await db.commit()
    await db.refresh(department)

    return department


@router.post("/import")
async def import_employees(
    file: UploadFile = File(...),
    current_user: dict = Depends(require_permission(Permission.EMPLOYEES_IMPORT)),
    db: AsyncSession = Depends(get_db)
):
    """Import employees from CSV file.

    RBAC: Only owner and hr_director can import employees.
    """
    company_id = UUID(current_user["company_id"])

    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported"
        )

    import csv
    import io

    content = await file.read()
    csv_content = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(csv_content))

    created = 0
    skipped = 0

    for row in reader:
        email = row.get('email', '').strip()
        if not email:
            skipped += 1
            continue

        # Check if exists
        existing = await db.execute(
            select(Employee)
            .where(Employee.company_id == company_id)
            .where(Employee.email == email)
        )
        if existing.scalar_one_or_none():
            skipped += 1
            continue

        employee = Employee(
            company_id=company_id,
            first_name=row.get('first_name', '').strip() or 'Unknown',
            last_name=row.get('last_name', '').strip() or 'Unknown',
            email=email,
            phone=row.get('phone', '').strip() or None,
            job_title=row.get('job_title', '').strip() or None,
        )
        db.add(employee)
        created += 1

    await db.commit()

    return {
        "message": f"Import completed: {created} created, {skipped} skipped",
        "created": created,
        "skipped": skipped
    }
